"""
File watcher component for monitoring file system changes
"""

import fnmatch
import logging
import os
from pathlib import Path
from typing import Callable, List

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

logger = logging.getLogger("files-db-mcp.file_watcher")


class FileChangeHandler(FileSystemEventHandler):
    """
    Handle file system events
    """

    def __init__(
        self, project_path: str, ignore_patterns: List[str], callback: Callable[[str, str], None]
    ):
        super().__init__()
        self.project_path = Path(project_path)
        self.ignore_patterns = ignore_patterns
        self.callback = callback

    def is_ignored(self, path: str) -> bool:
        """Check if a path should be ignored"""
        return any(fnmatch.fnmatch(path, pattern) for pattern in self.ignore_patterns)

    def on_created(self, event: FileSystemEvent):
        """Handle file creation event"""
        if event.is_directory:
            return

        rel_path = os.path.relpath(event.src_path, self.project_path)
        if not self.is_ignored(rel_path):
            self.callback("created", event.src_path)

    def on_modified(self, event: FileSystemEvent):
        """Handle file modification event"""
        if event.is_directory:
            return

        rel_path = os.path.relpath(event.src_path, self.project_path)
        if not self.is_ignored(rel_path):
            self.callback("modified", event.src_path)

    def on_deleted(self, event: FileSystemEvent):
        """Handle file deletion event"""
        if event.is_directory:
            return

        rel_path = os.path.relpath(event.src_path, self.project_path)
        if not self.is_ignored(rel_path):
            self.callback("deleted", event.src_path)

    def on_moved(self, event: FileSystemEvent):
        """Handle file move event"""
        if event.is_directory:
            return

        src_rel_path = os.path.relpath(event.src_path, self.project_path)
        dest_rel_path = os.path.relpath(event.dest_path, self.project_path)

        # Handle as delete + create
        if not self.is_ignored(src_rel_path):
            self.callback("deleted", event.src_path)

        if not self.is_ignored(dest_rel_path):
            self.callback("created", event.dest_path)


class FileWatcher:
    """
    Watch for file system changes in the project directory
    """

    def __init__(
        self,
        project_path: str,
        ignore_patterns: List[str],
        on_file_change: Callable[[str, str], None],
    ):
        self.project_path = project_path
        self.ignore_patterns = ignore_patterns
        self.on_file_change = on_file_change

        self.observer = None
        self.running = False

    def start(self):
        """Start watching for file changes"""
        if self.running:
            logger.warning("File watcher is already running")
            return

        try:
            logger.info(f"Starting file watcher for: {self.project_path}")

            event_handler = FileChangeHandler(
                project_path=self.project_path,
                ignore_patterns=self.ignore_patterns,
                callback=self.on_file_change,
            )

            self.observer = Observer()
            self.observer.schedule(event_handler, self.project_path, recursive=True)
            self.observer.start()

            self.running = True
            logger.info("File watcher started successfully")
        except Exception as e:
            logger.error(f"Error starting file watcher: {e!s}")
            raise

    def stop(self):
        """Stop watching for file changes"""
        if not self.running:
            logger.warning("File watcher is not running")
            return

        try:
            logger.info("Stopping file watcher")

            self.observer.stop()
            self.observer.join()

            self.running = False
            logger.info("File watcher stopped successfully")
        except Exception as e:
            logger.error(f"Error stopping file watcher: {e!s}")
            raise
