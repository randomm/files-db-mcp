import json
from unittest.mock import MagicMock

import pytest

from src.mcp_interface import MCPInterface


@pytest.fixture
def mock_vector_search():
    """Create a mock vector search engine"""
    mock = MagicMock()

    # Mock search method
    mock.search.return_value = [
        {
            "file_path": "/test/file.py",
            "file_type": "py",
            "content": "test content",
            "score": 0.95,
            "metadata": {"indexed_at": 1234567890},
        }
    ]

    # Mock get_file_content method
    mock.client.scroll.return_value.points = [MagicMock(payload={"content": "test file content"})]

    # Mock get_model_info method
    mock.get_model_info.return_value = {
        "model_name": "test_model",
        "vector_size": 384,
        "quantization": True,
        "collection_name": "files",
        "index_stats": {"total_points": 10},
    }

    # Mock change_model method
    mock.change_model.return_value = True

    return mock


@pytest.fixture
def mock_file_processor():
    """Create a mock file processor"""
    mock = MagicMock()
    
    # Set up mock methods
    mock.is_indexing_complete.return_value = True
    mock.get_indexing_progress.return_value = 100.0
    mock.get_files_indexed.return_value = 150
    mock.get_total_files.return_value = 200
    mock.schedule_indexing.return_value = None
    
    return mock


@pytest.fixture
def mcp_interface(mock_vector_search, mock_file_processor):
    """Create an MCP interface with mock dependencies"""
    return MCPInterface(vector_search=mock_vector_search, file_processor=mock_file_processor)


def test_register_functions(mcp_interface):
    """Test function registration"""
    functions = mcp_interface.functions

    assert "search_files" in functions
    assert "get_file_content" in functions
    assert "get_model_info" in functions
    assert "change_model" in functions
    assert "trigger_reindex" in functions
    assert "get_indexing_status" in functions


def test_search_files(mcp_interface, mock_vector_search):
    """Test search_files method"""
    result = mcp_interface.search_files(
        query="test query",
        limit=10,
        file_type="py",
        path_prefix="/test",
        search_params={"exact": True},
    )

    # Check that vector_search.search was called with correct parameters
    mock_vector_search.search.assert_called_once_with(
        query="test query",
        limit=10,
        file_type="py",
        path_prefix="/test",
        file_extensions=None,
        modified_after=None,
        modified_before=None,
        exclude_paths=None,
        custom_metadata=None,
        threshold=0.6,
        search_params={"exact": True},
    )

    # Check result
    assert result["success"] is True
    assert len(result["results"]) == 1
    assert result["count"] == 1
    assert "filters" in result


def test_get_file_content(mcp_interface, mock_vector_search):
    """Test get_file_content method"""
    result = mcp_interface.get_file_content("/test/file.py")

    # Check that vector_search.client.scroll was called
    mock_vector_search.client.scroll.assert_called_once()

    # Check result
    assert result["success"] is True
    assert result["file_path"] == "/test/file.py"
    assert result["content"] == "test file content"


def test_get_file_content_not_found(mcp_interface, mock_vector_search):
    """Test get_file_content method with file not found"""
    mock_vector_search.client.scroll.return_value.points = []

    result = mcp_interface.get_file_content("/test/nonexistent.py")

    # Check result
    assert result["success"] is False
    assert "error" in result


def test_get_model_info(mcp_interface, mock_vector_search):
    """Test get_model_info method"""
    result = mcp_interface.get_model_info()

    # Check that vector_search.get_model_info was called
    mock_vector_search.get_model_info.assert_called_once()

    # Check result
    assert result["success"] is True
    assert "model_info" in result
    assert result["model_info"]["model_name"] == "test_model"
    assert result["model_info"]["vector_size"] == 384


def test_change_model(mcp_interface, mock_vector_search):
    """Test change_model method"""
    result = mcp_interface.change_model(model_name="new_model", model_config={"device": "cuda"})

    # Check that vector_search.change_model was called with correct parameters
    mock_vector_search.change_model.assert_called_once_with("new_model", {"device": "cuda"})

    # Check result
    assert result["success"] is True
    assert "message" in result
    assert "model_info" in result


def test_change_model_failure(mcp_interface, mock_vector_search):
    """Test change_model method with failure"""
    mock_vector_search.change_model.return_value = False

    result = mcp_interface.change_model("invalid_model")

    # Check result
    assert result["success"] is False
    assert "error" in result


def test_handle_command_search(mcp_interface):
    """Test handle_command with search_files"""
    command = {
        "function": "search_files",
        "parameters": {"query": "test query", "limit": 5},
        "request_id": "123",
    }

    result = mcp_interface.handle_command(json.dumps(command))
    result_dict = json.loads(result)

    # Check result
    assert result_dict["success"] is True
    assert "results" in result_dict
    assert result_dict["request_id"] == "123"


def test_handle_command_unknown_function(mcp_interface):
    """Test handle_command with unknown function"""
    command = {"function": "unknown_function", "parameters": {}, "request_id": "123"}

    result = mcp_interface.handle_command(json.dumps(command))
    result_dict = json.loads(result)

    # Check result
    assert result_dict["success"] is False
    assert "error" in result_dict
    assert result_dict["request_id"] == "123"


def test_handle_command_invalid_json(mcp_interface):
    """Test handle_command with invalid JSON"""
    result = mcp_interface.handle_command("invalid json")
    result_dict = json.loads(result)

    # Check result
    assert result_dict["success"] is False
    assert "error" in result_dict


def test_trigger_reindex(mcp_interface, mock_file_processor):
    """Test trigger_reindex method"""
    # Test with incremental indexing
    result = mcp_interface.trigger_reindex(incremental=True)
    
    # Check file processor method calls
    mock_file_processor.is_indexing_complete.assert_called_once()
    mock_file_processor.schedule_indexing.assert_called_once_with(incremental=True)
    
    # Check result
    assert result["success"] is True
    assert "Started incremental reindexing" in result["message"]
    
    # Reset mocks for next test
    mock_file_processor.is_indexing_complete.reset_mock()
    mock_file_processor.schedule_indexing.reset_mock()
    
    # Test with full reindexing
    result = mcp_interface.trigger_reindex(incremental=False)
    
    # Check file processor method calls
    mock_file_processor.is_indexing_complete.assert_called_once()
    mock_file_processor.schedule_indexing.assert_called_once_with(incremental=False)
    
    # Check result
    assert result["success"] is True
    assert "Started full reindexing" in result["message"]
    
    # Test when indexing is already in progress
    mock_file_processor.is_indexing_complete.reset_mock()
    mock_file_processor.schedule_indexing.reset_mock()
    mock_file_processor.is_indexing_complete.return_value = False
    mock_file_processor.get_indexing_progress.return_value = 45.0
    
    result = mcp_interface.trigger_reindex()
    
    # Check result (should indicate indexing is already in progress)
    assert result["success"] is False
    assert "Indexing already in progress" in result["error"]
    assert result["progress"] == 45.0
    
    # Check that schedule_indexing was not called
    mock_file_processor.schedule_indexing.assert_not_called()


def test_get_indexing_status(mcp_interface, mock_file_processor):
    """Test get_indexing_status method"""
    result = mcp_interface.get_indexing_status()
    
    # Check file processor method calls
    mock_file_processor.is_indexing_complete.assert_called_once()
    mock_file_processor.get_indexing_progress.assert_called_once()
    mock_file_processor.get_files_indexed.assert_called_once()
    mock_file_processor.get_total_files.assert_called_once()
    
    # Check result
    assert result["success"] is True
    assert result["is_complete"] is True
    assert result["progress"] == 100.0
    assert result["files_indexed"] == 150
    assert result["total_files"] == 200
    
    # Test with no file processor
    mcp_without_processor = MCPInterface(vector_search=MagicMock(), file_processor=None)
    result = mcp_without_processor.get_indexing_status()
    
    # Check result
    assert result["success"] is False
    assert "File processor not available" in result["error"]
