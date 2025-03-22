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
def mcp_interface(mock_vector_search):
    """Create an MCP interface with a mock vector search engine"""
    return MCPInterface(mock_vector_search)


def test_register_functions(mcp_interface):
    """Test function registration"""
    functions = mcp_interface.functions

    assert "search_files" in functions
    assert "get_file_content" in functions
    assert "get_model_info" in functions
    assert "change_model" in functions


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
