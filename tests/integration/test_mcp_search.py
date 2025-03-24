"""
Integration tests for the MCP search functionality
"""

import json
from unittest.mock import MagicMock, patch

import pytest

from src.mcp_interface import MCPInterface
from src.vector_search import VectorSearch


@pytest.mark.integration
@patch("src.vector_search.QdrantClient")
@patch("src.vector_search.SentenceTransformer")
def test_mcp_search_integration(mock_transformer, mock_qdrant):
    """Test MCP search functionality end-to-end"""
    # Setup mocks
    mock_model = MagicMock()
    mock_model.encode.return_value = [0.1, 0.2, 0.3, 0.4, 0.5]
    mock_model.get_sentence_embedding_dimension.return_value = 5
    mock_transformer.return_value = mock_model

    mock_client = MagicMock()
    # Configure mock to return search results
    mock_client.search.return_value = [
        MagicMock(
            id="1",
            payload={
                "file_path": "src/main.py",
                "file_type": "py",
                "content": "def main():\n    print('Hello, world!')",
                "indexed_at": 1616493715.654321,
            },
            score=0.95,
        ),
        MagicMock(
            id="2",
            payload={
                "file_path": "src/utils.py",
                "file_type": "py",
                "content": "def helper():\n    return 'Helper function'",
                "indexed_at": 1616493716.123456,
            },
            score=0.85,
        ),
    ]
    mock_qdrant.return_value = mock_client

    # Create vector search engine
    vector_search = VectorSearch(
        host="localhost", port=6333, embedding_model="test-model", collection_name="test-collection"
    )

    # Create MCP interface
    mcp_interface = MCPInterface(vector_search=vector_search)

    # Simulate MCP command for search
    command = json.dumps(
        {
            "function": "search_files",
            "parameters": {"query": "main function", "limit": 2},
            "request_id": "test-123",
        }
    )

    # Process command
    response = mcp_interface.handle_command(command)
    response_data = json.loads(response)

    # Verify response
    assert response_data["success"] is True
    assert "results" in response_data
    assert len(response_data["results"]) == 2
    assert response_data["request_id"] == "test-123"

    # Verify first result
    first_result = response_data["results"][0]
    assert first_result["file_path"] == "src/main.py"
    assert first_result["file_type"] == "py"
    assert "def main()" in first_result["content"]
    assert first_result["score"] == 0.95

    # Verify search was called with correct parameters
    # For encode, check that the call contained the right query (other parameters may vary)
    assert any("main function" in str(call) for call in mock_model.encode.call_args_list)
    mock_client.search.assert_called_once()


@pytest.mark.integration
@patch("src.vector_search.QdrantClient")
@patch("src.vector_search.SentenceTransformer")
def test_mcp_search_with_filter(mock_transformer, mock_qdrant):
    """Test MCP search with file type filter"""
    # Setup mocks
    mock_model = MagicMock()
    mock_model.encode.return_value = [0.1, 0.2, 0.3, 0.4, 0.5]
    mock_model.get_sentence_embedding_dimension.return_value = 5
    mock_transformer.return_value = mock_model

    mock_client = MagicMock()
    # Configure mock to return search results
    mock_client.search.return_value = [
        MagicMock(
            id="1",
            payload={
                "file_path": "src/main.py",
                "file_type": "py",
                "content": "def main():\n    print('Hello, world!')",
                "indexed_at": 1616493715.654321,
            },
            score=0.95,
        )
    ]
    mock_qdrant.return_value = mock_client

    # Create vector search engine
    vector_search = VectorSearch(
        host="localhost", port=6333, embedding_model="test-model", collection_name="test-collection"
    )

    # Create MCP interface
    mcp_interface = MCPInterface(vector_search=vector_search)

    # Simulate MCP command for search with filter
    command = json.dumps(
        {
            "function": "search_files",
            "parameters": {"query": "main function", "limit": 5, "file_type": "py"},
            "request_id": "test-456",
        }
    )

    # Process command
    response = mcp_interface.handle_command(command)
    response_data = json.loads(response)

    # Verify response
    assert response_data["success"] is True
    assert "results" in response_data
    assert len(response_data["results"]) == 1
    assert response_data["request_id"] == "test-456"

    # Verify search was called with file_type filter (by using a spy)
    # First spy on the search method to verify it's called with the right parameters
    original_search = vector_search.search
    try:
        vector_search.search = MagicMock(wraps=original_search)
        
        # Repeat the command to use our spy
        mcp_interface.handle_command(command)
        
        # Now verify the parameters sent to search - using a more lenient check
        call_args = vector_search.search.call_args
        assert call_args is not None, "search method was not called"
        # Check that the required parameters were passed correctly
        assert call_args.kwargs['query'] == "main function"
        assert call_args.kwargs['limit'] == 5
        assert call_args.kwargs['file_type'] == "py"
    finally:
        # Restore the original method
        vector_search.search = original_search
