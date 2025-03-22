"""
File processor component for scanning, parsing, and indexing files
"""

import fnmatch
import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import List, Set

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

        # Load last indexed files if available
        self.load_state()

    def load_state(self):
        """Load state from disk"""
        state_file = self.data_dir / "file_processor_state.json"
        if state_file.exists():
            try:
                import json

                with open(state_file, "r") as f:
                    state = json.load(f)
                    self.last_indexed_files = set(state.get("indexed_files", []))
                    logger.info(
                        f"Loaded state: {len(self.last_indexed_files)} previously indexed files"
                    )
            except Exception as e:
                logger.error(f"Error loading state: {e!s}")

    def save_state(self):
        """Save state to disk"""
        state_file = self.data_dir / "file_processor_state.json"
        try:
            import json

            with open(state_file, "w") as f:
                json.dump(
                    {"indexed_files": list(self.last_indexed_files), "last_updated": time.time()}, f
                )
            logger.info(f"Saved state: {len(self.last_indexed_files)} indexed files")
        except Exception as e:
            logger.error(f"Error saving state: {e!s}")

    def is_ignored(self, file_path: str) -> bool:
        """Check if a file should be ignored"""
        return any(fnmatch.fnmatch(file_path, pattern) for pattern in self.ignore_patterns)

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

        logger.info(f"Found {len(file_list)} files to process")
        return file_list

    def process_file(self, rel_path: str) -> bool:
        """Process a single file for indexing"""
        try:
            file_path = os.path.join(self.project_path, rel_path)

            # Check if file exists and is readable
            if not os.path.isfile(file_path) or not os.access(file_path, os.R_OK):
                logger.warning(f"File {rel_path} is not accessible")
                return False

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

            # Add to vector search engine
            self.vector_search.index_file(rel_path, content)

            # Add to indexed files set
            self.last_indexed_files.add(rel_path)

            return True
        except Exception as e:
            logger.error(f"Error processing file {rel_path}: {e!s}")
            return False

    def index_files(self):
        """Index all files in the project directory"""
        if self.indexing_in_progress:
            logger.warning("Indexing already in progress")
            return

        self.indexing_in_progress = True

        try:
            # Get file list
            file_list = self.get_file_list()
            self.total_files = len(file_list)
            self.files_indexed = 0

            # Process files in parallel
            with ThreadPoolExecutor(max_workers=4) as executor:
                for success in tqdm(
                    executor.map(self.process_file, file_list),
                    total=self.total_files,
                    desc="Indexing files",
                ):
                    if success:
                        self.files_indexed += 1

                        # Report progress every 5% or 10 files, whichever is less frequent
                        report_frequency = max(1, min(int(self.total_files * 0.05), 10))
                        if self.files_indexed % report_frequency == 0:
                            logger.info(
                                f"Indexing progress: {self.files_indexed}/{self.total_files} files ({self.get_indexing_progress():.1f}%)"
                            )

            # Save state after indexing
            self.save_state()

            logger.info(f"Indexing complete: {self.files_indexed}/{self.total_files} files indexed")
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
        return self.files_indexed

    def get_total_files(self) -> int:
        """Get total number of files to index"""
        return self.total_files
        
    def schedule_indexing(self):
        """Schedule indexing to run in a background thread"""
        import threading
        thread = threading.Thread(target=self.index_files)
        thread.daemon = True
        thread.start()
