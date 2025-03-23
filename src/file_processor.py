"""
File processor component for scanning, parsing, and indexing files
"""

import fnmatch
import hashlib
import json
import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from tqdm import tqdm

logger = logging.getLogger("files-db-mcp.file_processor")


class FileProcessor:
    """
    Processes files in a project directory for indexing in the vector database
    """

    def __init__(self, vector_search, project_path: str, ignore_patterns: List[str], data_dir: str):
        self.vector_search = vector_search
        self.project_path = Path(project_path)
        self.ignore_patterns = ignore_patterns.copy()  # Create a copy to avoid modifying the original
        self.data_dir = Path(data_dir)

        # Indexing state
        self.indexing_in_progress = False
        self.files_indexed = 0
        self.total_files = 0
        self.last_indexed_files: Set[str] = set()
        
        # Enhanced file tracking: file path -> {hash, mtime, size}
        self.file_metadata: Dict[str, Dict[str, any]] = {}

        # Create data directory if it doesn't exist
        os.makedirs(self.data_dir, exist_ok=True)

        # Add state file to ignore patterns
        state_file_rel = os.path.relpath(str(self.data_dir / "file_processor_state.json"), self.project_path)
        if state_file_rel not in self.ignore_patterns:
            self.ignore_patterns.append(state_file_rel)
            # Also add a pattern for the directory if it's inside the project
            state_dir_rel = os.path.relpath(str(self.data_dir), self.project_path)
            if not state_dir_rel.startswith('..'):
                self.ignore_patterns.append(f"{state_dir_rel}/**")

        # Load state and file metadata if available
        self.load_state()

    def load_state(self):
        """Load state from disk"""
        state_file = self.data_dir / "file_processor_state.json"
        if state_file.exists():
            try:
                with open(state_file, "r") as f:
                    state = json.load(f)
                    self.last_indexed_files = set(state.get("indexed_files", []))
                    self.file_metadata = state.get("file_metadata", {})
                    logger.info(
                        f"Loaded state: {len(self.last_indexed_files)} previously indexed files"
                    )
            except Exception as e:
                logger.error(f"Error loading state: {e!s}")
                # Initialize empty metadata if loading fails
                self.file_metadata = {}

    def save_state(self):
        """Save state to disk"""
        state_file = self.data_dir / "file_processor_state.json"
        try:
            with open(state_file, "w") as f:
                json.dump(
                    {
                        "indexed_files": list(self.last_indexed_files), 
                        "file_metadata": self.file_metadata,
                        "last_updated": time.time()
                    }, 
                    f,
                    indent=2  # Pretty-print for readability
                )
            logger.info(f"Saved state: {len(self.last_indexed_files)} indexed files")
        except Exception as e:
            logger.error(f"Error saving state: {e!s}")

    def is_ignored(self, file_path: str) -> bool:
        """Check if a file should be ignored"""
        return any(fnmatch.fnmatch(file_path, pattern) for pattern in self.ignore_patterns)

    def compute_file_hash(self, file_path: str) -> Optional[str]:
        """
        Compute SHA-256 hash of file content
        
        Args:
            file_path: Absolute path to the file
            
        Returns:
            Hex digest of hash or None if file couldn't be read
        """
        try:
            hasher = hashlib.sha256()
            with open(file_path, 'rb') as f:
                # Read file in chunks to handle large files efficiently
                for chunk in iter(lambda: f.read(65536), b''):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception as e:
            logger.warning(f"Failed to compute hash for {file_path}: {e!s}")
            return None

    def get_file_stats(self, abs_path: str) -> Tuple[Optional[float], Optional[int], Optional[str]]:
        """
        Get file modification time, size, and hash
        
        Args:
            abs_path: Absolute path to file
            
        Returns:
            Tuple of (mtime, size, hash) or None values if stats couldn't be retrieved
        """
        try:
            # Get file stats
            stat_result = os.stat(abs_path)
            mtime = stat_result.st_mtime
            size = stat_result.st_size
            
            # Only compute hash for text files and limit by size
            # to avoid performance issues with large files
            if size < 10 * 1024 * 1024:  # 10 MB limit
                file_hash = self.compute_file_hash(abs_path)
            else:
                # For large files, use size+mtime instead of content hash
                file_hash = f"size:{size}_mtime:{mtime}"
                
            return mtime, size, file_hash
        except Exception as e:
            logger.warning(f"Failed to get stats for {abs_path}: {e!s}")
            return None, None, None

    def file_needs_update(self, rel_path: str) -> bool:
        """
        Check if a file needs to be reindexed based on its metadata
        
        Args:
            rel_path: Relative path to the file
            
        Returns:
            True if file needs updating, False otherwise
        """
        abs_path = os.path.join(self.project_path, rel_path)
        
        # If file doesn't exist, it definitely doesn't need updating
        if not os.path.isfile(abs_path):
            return False
            
        # If file is not in metadata or not in indexed files, it needs updating
        if rel_path not in self.file_metadata or rel_path not in self.last_indexed_files:
            return True
            
        # Get current file stats
        curr_mtime, curr_size, curr_hash = self.get_file_stats(abs_path)
        if curr_mtime is None:
            # If we can't get stats, assume it needs updating
            return True
            
        # Get stored metadata
        metadata = self.file_metadata.get(rel_path, {})
        stored_mtime = metadata.get('mtime')
        stored_size = metadata.get('size')
        stored_hash = metadata.get('hash')
        
        # If hash exists and is unchanged, file is the same
        if stored_hash and curr_hash and stored_hash == curr_hash:
            return False
            
        # If size and mtime match, probably unchanged
        if (stored_size == curr_size and stored_mtime == curr_mtime and 
            abs(curr_mtime - stored_mtime) < 0.001):  # mtime precision can vary
            return False
            
        # Otherwise, consider the file changed
        return True

    def get_file_list(self) -> List[str]:
        """Get list of files to index"""
        file_list = []
        logger.info(f"Scanning project directory: {self.project_path}")

        # Walk through all files in the project recursively
        for root, dirs, files in os.walk(self.project_path):
            # Filter directories in-place to avoid traversing ignored directories
            dirs[:] = [d for d in dirs if not self.is_ignored(d)]

            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, self.project_path)

                # Skip ignored files
                if self.is_ignored(rel_path):
                    continue

                file_list.append(rel_path)

        logger.info(f"Found {len(file_list)} files in project")
        return file_list

    def get_modified_files(self) -> Tuple[List[str], List[str], int]:
        """
        Get lists of new/modified files and calculate files to remove
        
        Returns:
            Tuple of (files_to_update, files_to_remove, total_files)
        """
        current_files = set(self.get_file_list())
        total_files = len(current_files)
        
        # Files that have been deleted since last indexing
        files_to_remove = list(self.last_indexed_files - current_files)
        
        # Files that might need updating (new or modified)
        files_to_check = list(current_files)
        
        # Filter to only get files that actually need updating based on metadata
        files_to_update = [f for f in files_to_check if self.file_needs_update(f)]
        
        logger.info(f"Found {len(files_to_update)} files that need indexing")
        logger.info(f"Found {len(files_to_remove)} files that have been deleted")
        
        return files_to_update, files_to_remove, total_files

    def process_file(self, rel_path: str) -> bool:
        """Process a single file for indexing"""
        try:
            file_path = os.path.join(self.project_path, rel_path)

            # Check if file exists and is readable
            if not os.path.isfile(file_path) or not os.access(file_path, os.R_OK):
                logger.warning(f"File {rel_path} is not accessible")
                return False

            # Get file metadata
            mtime, size, file_hash = self.get_file_stats(file_path)
            
            # Read file content
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                # Skip binary files
                logger.warning(f"File {rel_path} appears to be binary, skipping content extraction")
                content = f"[Binary file: {rel_path}]"
            
            # Simple content chunking for large files
            # If content is too large, truncate it to 5000 characters to avoid performance issues
            if len(content) > 5000:
                logger.debug(f"File {rel_path} is large ({len(content)} chars), truncating for indexing")
                content = content[:5000] + f"\n\n[Truncated: file is {len(content)} characters]"

            # Add to vector search engine with metadata
            metadata = {
                "mtime": mtime,
                "size": size,
                "hash": file_hash,
                "indexed_at": time.time()
            }
            
            # Add to vector search engine with metadata
            self.vector_search.index_file(rel_path, content, metadata)

            # Update our tracking info
            self.last_indexed_files.add(rel_path)
            self.file_metadata[rel_path] = metadata

            return True
        except Exception as e:
            logger.error(f"Error processing file {rel_path}: {e!s}")
            return False

    def index_files(self, incremental: bool = True):
        """
        Index files in the project directory
        
        Args:
            incremental: Whether to use incremental indexing (default: True)
        """
        if self.indexing_in_progress:
            logger.warning("Indexing already in progress")
            return

        self.indexing_in_progress = True

        try:
            start_time = time.time()
            
            if incremental and self.last_indexed_files:
                # Get files that need updating
                files_to_update, files_to_remove, self.total_files = self.get_modified_files()
                
                # Remove files that have been deleted
                if files_to_remove:
                    logger.info(f"Removing {len(files_to_remove)} deleted files from index")
                    for rel_path in files_to_remove:
                        self.vector_search.delete_file(rel_path)
                        if rel_path in self.last_indexed_files:
                            self.last_indexed_files.remove(rel_path)
                        if rel_path in self.file_metadata:
                            del self.file_metadata[rel_path]
                
                file_list = files_to_update
                logger.info(f"Running incremental indexing for {len(file_list)} modified files")
            else:
                # Full indexing
                file_list = self.get_file_list()
                self.total_files = len(file_list)
                logger.info(f"Running full indexing for {len(file_list)} files")
            
            self.files_indexed = 0

            # Process files in parallel
            with ThreadPoolExecutor(max_workers=4) as executor:
                for success in tqdm(
                    executor.map(self.process_file, file_list),
                    total=len(file_list),
                    desc="Indexing files",
                ):
                    if success:
                        self.files_indexed += 1

                        # Report progress every 5% or 10 files, whichever is less frequent
                        report_frequency = max(1, min(int(len(file_list) * 0.05), 10))
                        if self.files_indexed % report_frequency == 0:
                            progress_pct = (self.files_indexed / len(file_list) * 100) if file_list else 100.0
                            logger.info(
                                f"Indexing progress: {self.files_indexed}/{len(file_list)} files ({progress_pct:.1f}%)"
                            )

            # Save state after indexing
            self.save_state()

            elapsed_time = time.time() - start_time
            logger.info(f"Indexing complete: {self.files_indexed} files indexed in {elapsed_time:.2f} seconds")
        except Exception as e:
            logger.error(f"Error during indexing: {e!s}")
        finally:
            self.indexing_in_progress = False

    def handle_file_change(self, event_type: str, file_path: str):
        """Handle file change event from file watcher"""
        try:
            # Convert to relative path
            rel_path = os.path.relpath(file_path, self.project_path)

            # Skip ignored files
            if self.is_ignored(rel_path):
                return
                
            # Skip the state file itself to prevent infinite update loops
            state_file_path = str(self.data_dir / "file_processor_state.json")
            if os.path.abspath(file_path) == os.path.abspath(state_file_path):
                logger.debug(f"Ignoring change to state file: {file_path}")
                return

            logger.info(f"File change detected: {event_type} - {rel_path}")

            if event_type in ["created", "modified"]:
                # Add or update file
                self.process_file(rel_path)
            elif event_type == "deleted":
                # Remove file from index
                self.vector_search.delete_file(rel_path)
                if rel_path in self.last_indexed_files:
                    self.last_indexed_files.remove(rel_path)
                if rel_path in self.file_metadata:
                    del self.file_metadata[rel_path]

            # Save state after change
            self.save_state()
        except Exception as e:
            logger.error(f"Error handling file change {event_type} - {file_path}: {e!s}")

    def is_indexing_complete(self) -> bool:
        """Check if initial indexing is complete"""
        return not self.indexing_in_progress

    def get_indexing_progress(self) -> float:
        """Get indexing progress as a percentage"""
        if self.total_files == 0:
            return 100.0
        return (self.files_indexed / self.total_files) * 100.0

    def get_files_indexed(self) -> int:
        """Get number of files indexed"""
        return len(self.last_indexed_files)

    def get_total_files(self) -> int:
        """Get total number of files to index"""
        return self.total_files
        
    def schedule_indexing(self, incremental: bool = True):
        """
        Schedule indexing to run in a background thread
        
        Args:
            incremental: Whether to use incremental indexing (default: True)
        """
        import threading
        thread = threading.Thread(target=lambda: self.index_files(incremental=incremental))
        thread.daemon = True
        thread.start()
