"""
Unit tests for the file processor module
"""

import os
from unittest.mock import MagicMock, patch

from src.file_processor import FileProcessor


@patch("os.path.relpath")
@patch("os.makedirs")
def test_is_ignored(mock_makedirs, mock_relpath):
    """Test the is_ignored method"""
    # Mock os.makedirs to prevent file system operations
    mock_makedirs.return_value = None
    
    # Mock relpath to return predictable paths
    mock_relpath.side_effect = lambda path, start: f"rel/{os.path.basename(path)}"
    
    # Create a FileProcessor instance with mock dependencies
    vector_search = MagicMock()
    processor = FileProcessor(
        vector_search=vector_search,
        project_path="/test/project",
        ignore_patterns=[".git", "node_modules", "*.pyc"],
        data_dir="/test/data",
    )

    # Test ignored patterns
    assert processor.is_ignored(".git") is True
    # Note: With the optimized any() method, checking a path containing a pattern
    # is different from checking if a full path matches any pattern
    assert processor.is_ignored("node_modules") is True
    assert processor.is_ignored("some_file.pyc") is True

    # Test non-ignored patterns
    assert processor.is_ignored("src/main.py") is False
    assert processor.is_ignored("README.md") is False
    
    # Test that state file is automatically added to ignore patterns
    assert "rel/file_processor_state.json" in processor.ignore_patterns


@patch("builtins.open")
@patch("os.path.isfile")
@patch("os.access")
@patch("os.makedirs")
def test_process_file(mock_makedirs, mock_access, mock_isfile, mock_open):
    """Test the process_file method"""
    # Setup mocks
    mock_isfile.return_value = True
    mock_access.return_value = True
    mock_makedirs.return_value = None
    
    # Mock file reading
    mock_file_content = "This is the content of the test file"
    mock_file = MagicMock()
    mock_file.__enter__.return_value.read.return_value = mock_file_content
    mock_open.return_value = mock_file
    
    # Create mock vector search
    mock_vector_search = MagicMock()
    mock_vector_search.index_file.return_value = True

    # Create a FileProcessor instance
    processor = FileProcessor(
        vector_search=mock_vector_search,
        project_path="/test/project",
        ignore_patterns=[".git", "node_modules", "*.pyc"],
        data_dir="/test/data",
    )

    # Test successful processing
    result = processor.process_file("src/main.py")
    assert result is True
    mock_open.assert_called_once_with("/test/project/src/main.py", 'r', encoding='utf-8')
    # Use any() to check if the call was made, without strict metadata checking which can include timestamps
    assert any(call.args[0] == "src/main.py" and call.args[1] == mock_file_content 
               for call in mock_vector_search.index_file.call_args_list)

    # Test with large file content (exceeding 5000 chars)
    mock_vector_search.index_file.reset_mock()
    long_content = "x" * 6000
    mock_file.__enter__.return_value.read.return_value = long_content
    result = processor.process_file("src/large_file.py")
    assert result is True
    expected_truncated = long_content[:5000] + "\n\n[Truncated: file is 6000 characters]"
    # Check call with the truncated content
    assert any(call.args[0] == "src/large_file.py" and call.args[1] == expected_truncated
               for call in mock_vector_search.index_file.call_args_list)
    
    # Test with binary file (UnicodeDecodeError)
    mock_vector_search.index_file.reset_mock()
    mock_open.side_effect = UnicodeDecodeError('utf-8', b'binary_data', 0, 1, 'invalid start byte')
    result = processor.process_file("src/binary_file.bin")
    assert result is True
    assert any(call.args[0] == "src/binary_file.bin" and call.args[1] == "[Binary file: src/binary_file.bin]"
               for call in mock_vector_search.index_file.call_args_list)
    
    # Test with file that doesn't exist
    mock_isfile.return_value = False
    result = processor.process_file("nonexistent_file.py")
    assert result is False


@patch("os.makedirs")
def test_get_indexing_progress(mock_makedirs):
    """Test the get_indexing_progress method"""
    # Mock os.makedirs to prevent file system operations
    mock_makedirs.return_value = None
    
    # Create a FileProcessor instance with mock dependencies
    vector_search = MagicMock()
    processor = FileProcessor(
        vector_search=vector_search,
        project_path="/test/project",
        ignore_patterns=[".git", "node_modules", "*.pyc"],
        data_dir="/test/data",
    )

    # Test with zero total files
    processor.total_files = 0
    processor.files_indexed = 0
    assert processor.get_indexing_progress() == 100.0

    # Test with some files indexed
    processor.total_files = 10
    processor.files_indexed = 5
    assert processor.get_indexing_progress() == 50.0

    # Test with all files indexed
    processor.files_indexed = 10
    assert processor.get_indexing_progress() == 100.0


@patch("os.path.abspath")
@patch("os.path.relpath")
@patch("os.makedirs")
def test_handle_file_change_ignores_state_file(mock_makedirs, mock_relpath, mock_abspath):
    """Test that handle_file_change ignores the state file"""
    # Setup mocks
    mock_makedirs.return_value = None
    mock_relpath.return_value = "data/file_processor_state.json"
    
    # Mock the abspath to return the same value for both paths when it's the state file
    def mock_abspath_side_effect(path):
        if "file_processor_state.json" in path:
            return "/absolute/path/to/data/file_processor_state.json"
        return f"/absolute/path/to/{path}"
    
    mock_abspath.side_effect = mock_abspath_side_effect
    
    # Create mock vector search
    mock_vector_search = MagicMock()
    
    # Create a FileProcessor instance with a spy on process_file
    processor = FileProcessor(
        vector_search=mock_vector_search,
        project_path="/test/project",
        ignore_patterns=[],
        data_dir="/test/data",
    )
    processor.process_file = MagicMock()
    processor.save_state = MagicMock()
    
    # Test handling state file change - should be ignored
    state_file_path = os.path.join("/test/data", "file_processor_state.json")
    processor.handle_file_change("modified", state_file_path)
    
    # Verify that process_file was not called
    processor.process_file.assert_not_called()
    # Verify that save_state was not called
    processor.save_state.assert_not_called()
    
    # Test handling normal file change - should be processed
    normal_file_path = "/test/project/src/main.py"
    mock_relpath.return_value = "src/main.py"
    processor.handle_file_change("modified", normal_file_path)
    
    # Verify that process_file was called
    processor.process_file.assert_called_once_with("src/main.py")
    # Verify that save_state was called
    processor.save_state.assert_called_once()
