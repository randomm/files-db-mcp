"""
Unit tests for incremental indexing functionality
"""

import os
import json
from unittest.mock import MagicMock, patch, mock_open

import pytest

from src.file_processor import FileProcessor


@pytest.fixture
def mock_makedirs():
    """Mock os.makedirs to prevent file system errors"""
    with patch("os.makedirs") as mock:
        yield mock


@patch("src.file_processor.hashlib.sha256")
@patch("src.file_processor.os.stat")
@patch("builtins.open", new_callable=mock_open, read_data=b"test file content")
def test_compute_file_hash(mock_file_open, mock_stat, mock_sha256, mock_makedirs):
    """Test file hash computation"""
    # Set up mocks
    mock_hasher = MagicMock()
    mock_sha256.return_value = mock_hasher
    mock_hasher.hexdigest.return_value = "test_hash_digest"
    
    with patch.object(FileProcessor, 'load_state') as mock_load_state:
        # Create file processor with mocked load_state
        vector_search = MagicMock()
        processor = FileProcessor(
            vector_search=vector_search,
            project_path="/test/project",
            ignore_patterns=[],
            data_dir="/test/data",
        )
        
        # Reset the mock_file_open to clear any calls from load_state
        mock_file_open.reset_mock()
        
        # Test hash computation
        result = processor.compute_file_hash("/test/file.txt")
        
        # Verify
        mock_file_open.assert_called_once_with("/test/file.txt", "rb")
        assert mock_hasher.update.called
        assert result == "test_hash_digest"


@patch("src.file_processor.os.stat")
@patch("src.file_processor.open", new_callable=mock_open, read_data=b"test file content")
def test_get_file_stats(mock_file_open, mock_stat, mock_makedirs):
    """Test file stats retrieval"""
    # Set up mocks
    mock_stat_result = MagicMock()
    mock_stat_result.st_mtime = 12345.6789
    mock_stat_result.st_size = 1024
    mock_stat.return_value = mock_stat_result
    
    with patch.object(FileProcessor, 'load_state'):
        # Create file processor
        vector_search = MagicMock()
        processor = FileProcessor(
            vector_search=vector_search,
            project_path="/test/project",
            ignore_patterns=[],
            data_dir="/test/data",
        )
        
        # Mock hash computation
        processor.compute_file_hash = MagicMock(return_value="test_hash_digest")
    
    # Test getting file stats
    mtime, size, file_hash = processor.get_file_stats("/test/file.txt")
    
    # Verify
    mock_stat.assert_called_once_with("/test/file.txt")
    processor.compute_file_hash.assert_called_once_with("/test/file.txt")
    assert mtime == 12345.6789
    assert size == 1024
    assert file_hash == "test_hash_digest"
    
    # Test large file (> 10MB)
    mock_stat_result.st_size = 11 * 1024 * 1024
    mtime, size, file_hash = processor.get_file_stats("/test/large_file.bin")
    
    # For large files, we should not compute hash
    assert size == 11 * 1024 * 1024
    assert file_hash == f"size:{size}_mtime:{mtime}"


@patch("os.path.isfile")
@patch("os.path.join")
def test_file_needs_update(mock_join, mock_isfile, mock_makedirs):
    """Test file change detection logic"""
    # Set up mocks
    mock_isfile.return_value = True
    mock_join.side_effect = lambda *args: "/".join(str(arg) for arg in args)
    
    with patch.object(FileProcessor, 'load_state'):
        # Create file processor
        vector_search = MagicMock()
        processor = FileProcessor(
            vector_search=vector_search,
            project_path="/test/project",
            ignore_patterns=[],
            data_dir="/test/data",
        )
    
    # Mock file stats
    processor.get_file_stats = MagicMock(return_value=(12345.6789, 1024, "test_hash_digest"))
    
    # Test with file not in metadata (new file)
    assert processor.file_needs_update("src/new_file.py") is True
    
    # Test with file in metadata but modified
    processor.file_metadata = {
        "src/modified_file.py": {
            "mtime": 12345.0,
            "size": 1024,
            "hash": "old_hash_digest"
        }
    }
    processor.last_indexed_files = {"src/modified_file.py"}
    
    assert processor.file_needs_update("src/modified_file.py") is True
    
    # Test with file in metadata and unchanged
    processor.file_metadata = {
        "src/unchanged_file.py": {
            "mtime": 12345.6789,
            "size": 1024,
            "hash": "test_hash_digest"
        }
    }
    processor.last_indexed_files = {"src/unchanged_file.py"}
    
    assert processor.file_needs_update("src/unchanged_file.py") is False


@patch("src.file_processor.os.walk")
@patch("src.file_processor.os.path.relpath")
def test_get_modified_files(mock_relpath, mock_walk, mock_makedirs):
    """Test modified files detection"""
    # Set up mocks
    mock_walk.return_value = [
        ("/test/project", ["src"], ["README.md"]),
        ("/test/project/src", [], ["main.py", "utils.py", "config.py"]),
    ]
    mock_relpath.side_effect = lambda path, start: path.replace(str(start) + "/", "")
    
    with patch.object(FileProcessor, 'load_state'):
        # Create file processor
        vector_search = MagicMock()
        processor = FileProcessor(
            vector_search=vector_search,
            project_path="/test/project",
            ignore_patterns=[],
            data_dir="/test/data",
        )
    
    # Set up initial state with some previously indexed files
    processor.last_indexed_files = {
        "README.md", 
        "src/main.py", 
        "src/utils.py",
        "src/old_file.py"  # This file no longer exists
    }
    
    processor.file_metadata = {
        "README.md": {"mtime": 12345.0, "size": 512, "hash": "readme_hash"},
        "src/main.py": {"mtime": 12345.0, "size": 1024, "hash": "main_hash"},
        "src/utils.py": {"mtime": 12345.0, "size": 768, "hash": "utils_hash"},
        "src/old_file.py": {"mtime": 12345.0, "size": 256, "hash": "old_hash"},
    }
    
    # Mock file_needs_update to control which files appear modified
    def mock_needs_update(rel_path):
        # README.md and utils.py are modified, main.py is unchanged
        return rel_path in ["README.md", "src/utils.py", "src/config.py"]
    
    processor.file_needs_update = MagicMock(side_effect=mock_needs_update)
    
    # Test getting modified files
    files_to_update, files_to_remove, total_files = processor.get_modified_files()
    
    # Verify results
    assert sorted(files_to_update) == sorted(["README.md", "src/utils.py", "src/config.py"])
    assert sorted(files_to_remove) == ["src/old_file.py"]
    assert total_files == 4  # README.md, main.py, utils.py, config.py


@patch("json.dump")
@patch("builtins.open", new_callable=mock_open)
def test_save_state(mock_file_open, mock_json_dump, mock_makedirs):
    """Test state saving"""
    with patch.object(FileProcessor, 'load_state'):
        # Create file processor
        vector_search = MagicMock()
        processor = FileProcessor(
            vector_search=vector_search,
            project_path="/test/project",
            ignore_patterns=[],
            data_dir="/test/data",
        )
    
    # Set up state
    processor.last_indexed_files = {"file1.py", "file2.py"}
    processor.file_metadata = {
        "file1.py": {"mtime": 123.456, "size": 100, "hash": "hash1"},
        "file2.py": {"mtime": 789.012, "size": 200, "hash": "hash2"},
    }
    
    # Save state
    processor.save_state()
    
    # Verify - use any() to check for the file path since it might be a PosixPath object
    assert any(
        call.args[0] == "/test/data/file_processor_state.json" or str(call.args[0]) == "/test/data/file_processor_state.json"
        for call in mock_file_open.call_args_list
    )
    mock_json_dump.assert_called_once()
    
    # Check that we're saving the right data
    args, kwargs = mock_json_dump.call_args
    saved_data = args[0]
    assert "indexed_files" in saved_data
    assert "file_metadata" in saved_data
    assert "last_updated" in saved_data
    assert set(saved_data["indexed_files"]) == {"file1.py", "file2.py"}
    assert saved_data["file_metadata"] == processor.file_metadata


def test_load_state(mock_makedirs):
    """Test state loading"""
    # Mock Path.exists() to return True
    with patch("pathlib.Path.exists", return_value=True), \
         patch("builtins.open", mock_open(read_data='{"indexed_files": ["file1.py", "file2.py"], "file_metadata": {"file1.py": {"mtime": 123.456, "size": 100, "hash": "hash1"}, "file2.py": {"mtime": 789.012, "size": 200, "hash": "hash2"}}, "last_updated": 1234567890}')):
        
        # First patch load_state to avoid loading during init
        with patch.object(FileProcessor, 'load_state'):
            vector_search = MagicMock()
            processor = FileProcessor(
                vector_search=vector_search,
                project_path="/test/project",
                ignore_patterns=[],
                data_dir="/test/data",
            )
        
        # Then manually call load_state (the real one)
        processor.load_state()
        
        # Check that we loaded the right data
        assert processor.last_indexed_files == {"file1.py", "file2.py"}
        assert processor.file_metadata == {
            "file1.py": {"mtime": 123.456, "size": 100, "hash": "hash1"},
            "file2.py": {"mtime": 789.012, "size": 200, "hash": "hash2"},
        }


@patch("src.file_processor.ThreadPoolExecutor")
def test_incremental_indexing(mock_thread_pool, mock_makedirs):
    """Test incremental indexing functionality"""
    # Create mocks
    vector_search = MagicMock()
    executor = MagicMock()
    mock_thread_pool.return_value.__enter__.return_value = executor
    executor.map.return_value = [True, True, False]  # 2 successful, 1 failed
    
    with patch.object(FileProcessor, 'load_state'):
        # Create file processor
        processor = FileProcessor(
            vector_search=vector_search,
            project_path="/test/project",
            ignore_patterns=[],
            data_dir="/test/data",
        )
    
    # Create a replacement set of test files that exists
    processor.last_indexed_files = {"file1.py", "file2.py", "file3.py", "old_file.py"}
    
    # Mock methods - do this AFTER initializing the processor
    processor.get_modified_files = MagicMock(return_value=(
        ["file1.py", "file2.py", "file3.py"],  # files to update
        ["old_file.py"],  # files to remove
        4  # total files
    ))
    processor.get_file_list = MagicMock(return_value=["file1.py", "file2.py", "file3.py", "file4.py"])
    processor.save_state = MagicMock()
    
    # Test incremental indexing (default)
    processor.index_files(incremental=True)
    
    # Verify that we used the get_modified_files results
    processor.get_modified_files.assert_called_once()
    assert processor.total_files == 4
    
    # Check if vector_search.delete_file was called for removed files
    vector_search.delete_file.assert_called_once_with("old_file.py")
    
    # Verify that we processed the right files
    executor.map.assert_called_once_with(processor.process_file, ["file1.py", "file2.py", "file3.py"])
    
    # Check if save_state was called
    processor.save_state.assert_called_once()
    
    # Check that files_indexed was updated correctly
    assert processor.files_indexed == 2  # Only the successful ones
    
    # Reset mocks for testing full indexing
    processor.get_modified_files.reset_mock()
    vector_search.delete_file.reset_mock()
    executor.map.reset_mock()
    processor.save_state.reset_mock()
    
    # Test full indexing
    processor.index_files(incremental=False)
    
    # Verify that for full indexing, we didn't use get_modified_files
    processor.get_modified_files.assert_not_called()
    
    # But we did call get_file_list
    processor.get_file_list.assert_called()
    
    # And we processed all files
    executor.map.assert_called_once_with(processor.process_file, ["file1.py", "file2.py", "file3.py", "file4.py"])