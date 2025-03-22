"""
Unit tests for the file watcher module
"""

import os
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest
from watchdog.events import FileSystemEvent
from watchdog.observers import Observer

from src.file_watcher import FileChangeHandler, FileWatcher


@pytest.fixture
def mock_callback():
    """Create a mock callback function"""
    return MagicMock()


@pytest.fixture
def file_change_handler(mock_callback):
    """Create a FileChangeHandler instance"""
    return FileChangeHandler(
        project_path="/test/project",
        ignore_patterns=[".git", "node_modules", "*.pyc"],
        callback=mock_callback,
    )


@pytest.fixture
def file_watcher(mock_callback):
    """Create a FileWatcher instance"""
    return FileWatcher(
        project_path="/test/project",
        ignore_patterns=[".git", "node_modules", "*.pyc"],
        on_file_change=mock_callback,
    )


def test_file_change_handler_init(file_change_handler, mock_callback):
    """Test FileChangeHandler initialization"""
    assert file_change_handler.project_path == Path("/test/project")
    assert file_change_handler.ignore_patterns == [".git", "node_modules", "*.pyc"]
    assert file_change_handler.callback == mock_callback


def test_is_ignored(file_change_handler):
    """Test is_ignored method"""
    # Define a custom side effect for fnmatch.fnmatch that follows the actual pattern matching logic
    def custom_fnmatch(path, pattern):
        if pattern == ".git" and ".git" in path:
            return True
        if pattern == "node_modules" and "node_modules" in path:
            return True
        if pattern == "*.pyc" and path.endswith(".pyc"):
            return True
        return False
    
    # Patch fnmatch.fnmatch to use our custom matcher
    with patch("fnmatch.fnmatch", side_effect=custom_fnmatch):
        # Test ignored patterns
        assert file_change_handler.is_ignored(".git/HEAD") is True
        assert file_change_handler.is_ignored("node_modules/package.json") is True
        assert file_change_handler.is_ignored("src/main.pyc") is True

        # Test non-ignored patterns
        assert file_change_handler.is_ignored("src/main.py") is False
        assert file_change_handler.is_ignored("README.md") is False


def test_on_created(file_change_handler, mock_callback):
    """Test on_created method"""
    # Create mock event
    event = Mock(spec=FileSystemEvent)
    event.is_directory = False
    event.src_path = "/test/project/src/main.py"

    # Handle event
    with patch("os.path.relpath", return_value="src/main.py"):
        # Patch is_ignored to return False for this test
        with patch.object(file_change_handler, "is_ignored", return_value=False):
            file_change_handler.on_created(event)

    # Check callback was called
    mock_callback.assert_called_once_with("created", "/test/project/src/main.py")

    # Test with directory event
    event.is_directory = True
    mock_callback.reset_mock()
    file_change_handler.on_created(event)
    mock_callback.assert_not_called()

    # Test with ignored path
    event.is_directory = False
    mock_callback.reset_mock()
    with patch("os.path.relpath", return_value=".git/HEAD"):
        # Patch is_ignored to return True for this test
        with patch.object(file_change_handler, "is_ignored", return_value=True):
            file_change_handler.on_created(event)
    mock_callback.assert_not_called()


def test_on_modified(file_change_handler, mock_callback):
    """Test on_modified method"""
    # Create mock event
    event = Mock(spec=FileSystemEvent)
    event.is_directory = False
    event.src_path = "/test/project/src/main.py"

    # Handle event
    with patch("os.path.relpath", return_value="src/main.py"):
        # Patch is_ignored to return False for this test
        with patch.object(file_change_handler, "is_ignored", return_value=False):
            file_change_handler.on_modified(event)

    # Check callback was called
    mock_callback.assert_called_once_with("modified", "/test/project/src/main.py")

    # Test with directory event
    event.is_directory = True
    mock_callback.reset_mock()
    file_change_handler.on_modified(event)
    mock_callback.assert_not_called()

    # Test with ignored path
    event.is_directory = False
    mock_callback.reset_mock()
    with patch("os.path.relpath", return_value=".git/HEAD"):
        # Patch is_ignored to return True for this test
        with patch.object(file_change_handler, "is_ignored", return_value=True):
            file_change_handler.on_modified(event)
    mock_callback.assert_not_called()


def test_on_deleted(file_change_handler, mock_callback):
    """Test on_deleted method"""
    # Create mock event
    event = Mock(spec=FileSystemEvent)
    event.is_directory = False
    event.src_path = "/test/project/src/main.py"

    # Handle event
    with patch("os.path.relpath", return_value="src/main.py"):
        # Patch is_ignored to return False for this test
        with patch.object(file_change_handler, "is_ignored", return_value=False):
            file_change_handler.on_deleted(event)

    # Check callback was called
    mock_callback.assert_called_once_with("deleted", "/test/project/src/main.py")

    # Test with directory event
    event.is_directory = True
    mock_callback.reset_mock()
    file_change_handler.on_deleted(event)
    mock_callback.assert_not_called()

    # Test with ignored path
    event.is_directory = False
    mock_callback.reset_mock()
    with patch("os.path.relpath", return_value=".git/HEAD"):
        # Patch is_ignored to return True for this test
        with patch.object(file_change_handler, "is_ignored", return_value=True):
            file_change_handler.on_deleted(event)
    mock_callback.assert_not_called()


def test_on_moved(file_change_handler, mock_callback):
    """Test on_moved method"""
    # Create mock event
    event = Mock(spec=FileSystemEvent)
    event.is_directory = False
    event.src_path = "/test/project/src/old.py"
    event.dest_path = "/test/project/src/new.py"

    # Handle event - both paths not ignored
    with patch("os.path.relpath", side_effect=["src/old.py", "src/new.py"]):
        with patch.object(file_change_handler, "is_ignored", return_value=False):
            file_change_handler.on_moved(event)

    # Check callback was called
    assert mock_callback.call_count == 2
    mock_callback.assert_any_call("deleted", "/test/project/src/old.py")
    mock_callback.assert_any_call("created", "/test/project/src/new.py")

    # Test with directory event
    event.is_directory = True
    mock_callback.reset_mock()
    file_change_handler.on_moved(event)
    mock_callback.assert_not_called()

    # Test with ignored source path, non-ignored destination
    event.is_directory = False
    mock_callback.reset_mock()
    with patch("os.path.relpath", side_effect=[".git/HEAD", "src/new.py"]):
        with patch.object(file_change_handler, "is_ignored", side_effect=[True, False]):
            file_change_handler.on_moved(event)
    mock_callback.assert_called_once_with("created", "/test/project/src/new.py")

    # Test with non-ignored source path, ignored destination
    mock_callback.reset_mock()
    with patch("os.path.relpath", side_effect=["src/old.py", ".git/HEAD"]):
        with patch.object(file_change_handler, "is_ignored", side_effect=[False, True]):
            file_change_handler.on_moved(event)
    mock_callback.assert_called_once_with("deleted", "/test/project/src/old.py")

    # Test with both paths ignored
    mock_callback.reset_mock()
    with patch("os.path.relpath", side_effect=[".git/HEAD", "node_modules/package.json"]):
        with patch.object(file_change_handler, "is_ignored", return_value=True):
            file_change_handler.on_moved(event)
    mock_callback.assert_not_called()


def test_file_watcher_init(file_watcher, mock_callback):
    """Test FileWatcher initialization"""
    assert file_watcher.project_path == "/test/project"
    assert file_watcher.ignore_patterns == [".git", "node_modules", "*.pyc"]
    assert file_watcher.on_file_change == mock_callback
    assert file_watcher.observer is None
    assert file_watcher.running is False


@patch("src.file_watcher.FileChangeHandler")
@patch("src.file_watcher.Observer")
def test_start(mock_observer_class, mock_handler_class, file_watcher, mock_callback):
    """Test start method"""
    # Mock observer instance
    mock_observer = mock_observer_class.return_value

    # Start the watcher
    file_watcher.start()

    # Check that handler was created correctly
    mock_handler_class.assert_called_once_with(
        project_path="/test/project",
        ignore_patterns=[".git", "node_modules", "*.pyc"],
        callback=mock_callback,
    )

    # Check that observer was configured correctly
    mock_observer_class.assert_called_once()
    mock_observer.schedule.assert_called_once()
    mock_observer.start.assert_called_once()

    # Check state
    assert file_watcher.running is True
    assert file_watcher.observer == mock_observer

    # Test starting again
    with patch("logging.Logger.warning") as mock_warning:
        file_watcher.start()
        mock_warning.assert_called_once()
        assert mock_observer.start.call_count == 1  # Still only called once


@patch("src.file_watcher.Observer")
def test_stop(mock_observer_class, file_watcher):
    """Test stop method"""
    # Mock observer instance
    mock_observer = mock_observer_class.return_value
    file_watcher.observer = mock_observer
    file_watcher.running = True

    # Stop the watcher
    file_watcher.stop()

    # Check that observer was stopped correctly
    mock_observer.stop.assert_called_once()
    mock_observer.join.assert_called_once()

    # Check state
    assert file_watcher.running is False

    # Test stopping again
    mock_observer.stop.reset_mock()
    mock_observer.join.reset_mock()
    with patch("logging.Logger.warning") as mock_warning:
        file_watcher.stop()
        mock_warning.assert_called_once()
        assert not mock_observer.stop.called
        assert not mock_observer.join.called


@patch("src.file_watcher.Observer")
def test_start_exception(mock_observer_class, file_watcher):
    """Test exception handling in start method"""
    # Mock observer to raise an exception
    mock_observer = mock_observer_class.return_value
    mock_observer.start.side_effect = Exception("Test error")

    # Start the watcher
    with pytest.raises(Exception):
        file_watcher.start()

    # Check state
    assert file_watcher.running is False


@patch("src.file_watcher.Observer")
def test_stop_exception(mock_observer_class, file_watcher):
    """Test exception handling in stop method"""
    # Mock observer to raise an exception
    mock_observer = mock_observer_class.return_value
    mock_observer.stop.side_effect = Exception("Test error")
    file_watcher.observer = mock_observer
    file_watcher.running = True

    # Stop the watcher
    with pytest.raises(Exception):
        file_watcher.stop()

    # Check state
    assert file_watcher.running is True