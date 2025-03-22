"""
Unit tests for the file processor module
"""

from unittest.mock import MagicMock, patch

from src.file_processor import FileProcessor


@patch("os.makedirs")
def test_is_ignored(mock_makedirs):
    """Test the is_ignored method"""
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

    # Test ignored patterns
    assert processor.is_ignored(".git") is True
    # Note: With the optimized any() method, checking a path containing a pattern
    # is different from checking if a full path matches any pattern
    assert processor.is_ignored("node_modules") is True
    assert processor.is_ignored("some_file.pyc") is True

    # Test non-ignored patterns
    assert processor.is_ignored("src/main.py") is False
    assert processor.is_ignored("README.md") is False


@patch("os.path.isfile")
@patch("os.access")
@patch("os.makedirs")
def test_process_file(mock_makedirs, mock_access, mock_isfile):
    """Test the process_file method"""
    # Setup mocks
    mock_isfile.return_value = True
    mock_access.return_value = True
    mock_makedirs.return_value = None
    
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
    mock_vector_search.index_file.assert_called_once_with("src/main.py", "File content placeholder")

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
