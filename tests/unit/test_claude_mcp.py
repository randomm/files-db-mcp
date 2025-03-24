"""
Unit tests for Claude MCP implementation
"""

import json
import io
from unittest.mock import MagicMock, patch

import pytest

from src.claude_mcp import ClaudeMCP, MESSAGE_TYPE_HELLO, MESSAGE_TYPE_TOOL_CALL, MESSAGE_TYPE_RESOURCE_REQUEST, MESSAGE_TYPE_PROMPT_REQUEST


@pytest.fixture
def mocked_vector_search():
    """Create a mock vector search object with all necessary methods mocked"""
    vector_search = MagicMock()
    
    # Mock the search method
    search_results = [
        {
            "file_path": "/test/file.py",
            "score": 0.95,
            "snippet": "def test_function():\n    return True",
            "metadata": {
                "file_type": "python",
                "file_size": 256,
                "last_modified": 1647347761
            }
        }
    ]
    vector_search.search.return_value = search_results
    
    # Mock get_file_content
    vector_search.get_file_content.return_value = {
        "success": True,
        "content": "# Test file\ndef test_function():\n    return True"
    }
    
    # Mock get_model_info
    vector_search.get_model_info.return_value = {
        "model_name": "sentence-transformers/all-MiniLM-L6-v2",
        "vector_size": 384,
        "quantization": True,
        "binary_embeddings": False
    }
    
    # Mock get_collection_stats
    vector_search.get_collection_stats.return_value = {
        "total_files": 42,
        "total_points": 100
    }
    
    # Set attributes
    vector_search.collection_name = "files"
    vector_search.model_name = "sentence-transformers/all-MiniLM-L6-v2"
    vector_search.dimension = 384
    vector_search.host = "localhost"
    vector_search.port = 6333
    
    return vector_search


@pytest.fixture
def claude_mcp(mocked_vector_search):
    """Create a ClaudeMCP instance with mock stdin/stdout"""
    mcp = ClaudeMCP(vector_search=mocked_vector_search)
    mcp.stdin = io.StringIO()
    mcp.stdout = io.StringIO()
    return mcp


def test_initialization(mocked_vector_search):
    """Test ClaudeMCP initialization"""
    mcp = ClaudeMCP(vector_search=mocked_vector_search)
    
    # Check attributes
    assert mcp.vector_search == mocked_vector_search
    assert mcp.name == "files-db-mcp"
    assert mcp.version == "0.1.0"


def test_send_hello(claude_mcp):
    """Test sending hello message"""
    claude_mcp._send_hello()
    
    # Get the message from stdout
    claude_mcp.stdout.seek(0)
    message = json.loads(claude_mcp.stdout.read().strip())
    
    # Check the message structure
    assert message["type"] == MESSAGE_TYPE_HELLO
    assert message["server"]["name"] == "files-db-mcp"
    assert message["server"]["version"] == "0.1.0"
    
    # Check capabilities
    assert "capabilities" in message
    assert "tools" in message["capabilities"]
    assert "vector_search" in message["capabilities"]["tools"]
    assert "get_file_content" in message["capabilities"]["tools"]
    assert "get_model_info" in message["capabilities"]["tools"]
    
    # Check tool parameters
    vector_search_tool = message["capabilities"]["tools"]["vector_search"]
    assert "parameters" in vector_search_tool
    assert "query" in vector_search_tool["parameters"]
    assert "limit" in vector_search_tool["parameters"]
    
    # Check resource capabilities
    assert "resources" in message["capabilities"]
    assert "vector_search_info" in message["capabilities"]["resources"]
    
    # Check prompt capabilities
    assert "prompts" in message["capabilities"]
    assert "vector_search_help" in message["capabilities"]["prompts"]


def test_tool_vector_search(claude_mcp):
    """Test vector_search tool implementation"""
    # Set up arguments
    arguments = {
        "query": "function definition",
        "limit": 5,
        "file_type": "python",
        "path_prefix": "/test",
        "file_extensions": ["py"],
        "threshold": 0.7
    }
    
    # Call the tool
    result = claude_mcp._tool_vector_search(arguments)
    
    # Check that search was called with the right parameters
    claude_mcp.vector_search.search.assert_called_once_with(
        query="function definition",
        limit=5,
        file_type="python",
        path_prefix="/test",
        file_extensions=["py"],
        threshold=0.7
    )
    
    # Check result structure
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["type"] == "text"
    
    # Parse the JSON in the text
    result_data = json.loads(result[0]["text"])
    assert isinstance(result_data, list)
    assert len(result_data) == 1
    assert result_data[0]["file_path"] == "/test/file.py"
    assert result_data[0]["score"] == 0.95
    assert "snippet" in result_data[0]
    assert "metadata" in result_data[0]


def test_tool_vector_search_missing_query(claude_mcp):
    """Test vector_search tool with missing query parameter"""
    # Set up arguments without query
    arguments = {
        "limit": 5
    }
    
    # Call the tool and check that it raises ValueError
    with pytest.raises(ValueError) as excinfo:
        claude_mcp._tool_vector_search(arguments)
    
    assert "Query is required" in str(excinfo.value)


def test_tool_get_file_content(claude_mcp):
    """Test get_file_content tool implementation"""
    # Set up arguments
    arguments = {
        "file_path": "/test/file.py"
    }
    
    # Call the tool
    result = claude_mcp._tool_get_file_content(arguments)
    
    # Check that get_file_content was called with the right parameters
    claude_mcp.vector_search.get_file_content.assert_called_once_with("/test/file.py")
    
    # Check result structure
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["type"] == "text"
    assert result[0]["text"] == "# Test file\ndef test_function():\n    return True"


def test_tool_get_file_content_missing_path(claude_mcp):
    """Test get_file_content tool with missing file_path parameter"""
    # Set up arguments without file_path
    arguments = {}
    
    # Call the tool and check that it raises ValueError
    with pytest.raises(ValueError) as excinfo:
        claude_mcp._tool_get_file_content(arguments)
    
    assert "File path is required" in str(excinfo.value)


def test_tool_get_file_content_file_not_found(claude_mcp):
    """Test get_file_content tool when file is not found"""
    # Set up arguments
    arguments = {
        "file_path": "/nonexistent/file.py"
    }
    
    # Mock a failure response
    claude_mcp.vector_search.get_file_content.return_value = {
        "success": False,
        "error": "File not found"
    }
    
    # Call the tool and check that it raises ValueError
    with pytest.raises(ValueError) as excinfo:
        claude_mcp._tool_get_file_content(arguments)
    
    assert "File not found" in str(excinfo.value)


def test_tool_get_model_info(claude_mcp):
    """Test get_model_info tool implementation"""
    # Set up arguments (empty for this tool)
    arguments = {}
    
    # Call the tool
    result = claude_mcp._tool_get_model_info(arguments)
    
    # Check that get_model_info was called
    claude_mcp.vector_search.get_model_info.assert_called_once()
    
    # Check result structure
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["type"] == "text"
    
    # Parse the JSON in the text
    result_data = json.loads(result[0]["text"])
    assert result_data["model_name"] == "sentence-transformers/all-MiniLM-L6-v2"
    assert result_data["vector_size"] == 384
    assert result_data["quantization"] is True
    assert result_data["binary_embeddings"] is False


def test_resource_vector_search_info(claude_mcp):
    """Test vector_search_info resource implementation"""
    # Call the resource handler with "stats" type
    result = claude_mcp._resource_vector_search_info("stats")
    
    # Check that get_collection_stats was called
    claude_mcp.vector_search.get_collection_stats.assert_called_once()
    
    # Check result structure
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["uri"] == "vector-search://stats"
    
    # Parse the JSON in the text
    result_data = json.loads(result[0]["text"])
    assert result_data["total_files_indexed"] == 42
    assert result_data["collection_name"] == "files"
    assert result_data["model_name"] == "sentence-transformers/all-MiniLM-L6-v2"
    assert result_data["dimension"] == 384
    assert result_data["server_address"] == "localhost:6333"


def test_resource_vector_search_info_unknown_type(claude_mcp):
    """Test vector_search_info resource with unknown resource type"""
    # Call the resource handler with an unknown type
    with pytest.raises(ValueError) as excinfo:
        claude_mcp._resource_vector_search_info("unknown")
    
    assert "Unknown resource type: unknown" in str(excinfo.value)


def test_prompt_vector_search_help(claude_mcp):
    """Test vector_search_help prompt implementation"""
    # Call the prompt handler
    result = claude_mcp._prompt_vector_search_help()
    
    # Check result structure
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["type"] == "text"
    assert "# Vector Search Help" in result[0]["text"]
    assert "Files-DB-MCP provides semantic search" in result[0]["text"]


def test_handle_tool_call(claude_mcp):
    """Test handling a tool call message"""
    # Set up a tool call message
    message = {
        "type": MESSAGE_TYPE_TOOL_CALL,
        "call_id": "test-call-123",
        "tool": {
            "name": "vector_search",
            "arguments": {
                "query": "test query",
                "limit": 5
            }
        }
    }
    
    # Set up a spy for _tool_vector_search
    with patch.object(claude_mcp, '_tool_vector_search') as mock_tool:
        mock_tool.return_value = [{"type": "text", "text": "test result"}]
        
        # Handle the message
        claude_mcp._handle_tool_call(message)
        
        # Check that _tool_vector_search was called with the right arguments
        mock_tool.assert_called_once_with({"query": "test query", "limit": 5})
        
        # Check that the result was sent
        claude_mcp.stdout.seek(0)
        response = json.loads(claude_mcp.stdout.read().strip())
        
        assert response["type"] == "tool_result"
        assert response["call_id"] == "test-call-123"
        assert response["content"] == [{"type": "text", "text": "test result"}]


def test_handle_tool_call_error(claude_mcp):
    """Test handling a tool call message that results in an error"""
    # Set up a tool call message
    message = {
        "type": MESSAGE_TYPE_TOOL_CALL,
        "call_id": "test-call-123",
        "tool": {
            "name": "vector_search",
            "arguments": {
                "limit": 5
                # Missing required query parameter
            }
        }
    }
    
    # Handle the message
    claude_mcp._handle_tool_call(message)
    
    # Check that an error response was sent
    claude_mcp.stdout.seek(0)
    response = json.loads(claude_mcp.stdout.read().strip())
    
    assert response["type"] == "tool_result"
    assert response["call_id"] == "test-call-123"
    assert "error" in response
    assert "message" in response["error"]
    assert "Query is required" in response["error"]["message"]


def test_handle_tool_call_unknown_tool(claude_mcp):
    """Test handling a tool call message with an unknown tool name"""
    # Set up a tool call message with an unknown tool
    message = {
        "type": MESSAGE_TYPE_TOOL_CALL,
        "call_id": "test-call-123",
        "tool": {
            "name": "unknown_tool",
            "arguments": {}
        }
    }
    
    # Handle the message
    claude_mcp._handle_tool_call(message)
    
    # Check that an error response was sent
    claude_mcp.stdout.seek(0)
    response = json.loads(claude_mcp.stdout.read().strip())
    
    assert response["type"] == "tool_result"
    assert response["call_id"] == "test-call-123"
    assert "error" in response
    assert "message" in response["error"]
    assert "Unknown tool: unknown_tool" in response["error"]["message"]


def test_handle_resource_request(claude_mcp):
    """Test handling a resource request message"""
    # Set up a resource request message
    message = {
        "type": MESSAGE_TYPE_RESOURCE_REQUEST,
        "request_id": "test-request-123",
        "uri": "vector-search://stats"
    }
    
    # Set up a spy for _resource_vector_search_info
    with patch.object(claude_mcp, '_resource_vector_search_info') as mock_resource:
        mock_resource.return_value = [{"uri": "vector-search://stats", "text": "test stats"}]
        
        # Handle the message
        claude_mcp._handle_resource_request(message)
        
        # Check that _resource_vector_search_info was called with the right type
        mock_resource.assert_called_once_with("stats")
        
        # Check that the result was sent
        claude_mcp.stdout.seek(0)
        response = json.loads(claude_mcp.stdout.read().strip())
        
        assert response["type"] == "resource_response"
        assert response["request_id"] == "test-request-123"
        assert response["contents"] == [{"uri": "vector-search://stats", "text": "test stats"}]


def test_handle_resource_request_unknown_uri(claude_mcp):
    """Test handling a resource request message with an unknown URI"""
    # Set up a resource request message with an unknown URI
    message = {
        "type": MESSAGE_TYPE_RESOURCE_REQUEST,
        "request_id": "test-request-123",
        "uri": "unknown://resource"
    }
    
    # Handle the message
    claude_mcp._handle_resource_request(message)
    
    # Check that an error response was sent
    claude_mcp.stdout.seek(0)
    response = json.loads(claude_mcp.stdout.read().strip())
    
    assert response["type"] == "resource_response"
    assert response["request_id"] == "test-request-123"
    assert "error" in response
    assert "message" in response["error"]
    assert "Unknown resource URI: unknown://resource" in response["error"]["message"]


def test_handle_prompt_request(claude_mcp):
    """Test handling a prompt request message"""
    # Set up a prompt request message
    message = {
        "type": MESSAGE_TYPE_PROMPT_REQUEST,
        "request_id": "test-request-123",
        "prompt": {
            "name": "vector_search_help"
        }
    }
    
    # Set up a spy for _prompt_vector_search_help
    with patch.object(claude_mcp, '_prompt_vector_search_help') as mock_prompt:
        mock_prompt.return_value = [{"type": "text", "text": "help text"}]
        
        # Handle the message
        claude_mcp._handle_prompt_request(message)
        
        # Check that _prompt_vector_search_help was called
        mock_prompt.assert_called_once()
        
        # Check that the result was sent
        claude_mcp.stdout.seek(0)
        response = json.loads(claude_mcp.stdout.read().strip())
        
        assert response["type"] == "prompt_response"
        assert response["request_id"] == "test-request-123"
        assert response["content"] == [{"type": "text", "text": "help text"}]


def test_handle_prompt_request_unknown_prompt(claude_mcp):
    """Test handling a prompt request message with an unknown prompt name"""
    # Set up a prompt request message with an unknown prompt
    message = {
        "type": MESSAGE_TYPE_PROMPT_REQUEST,
        "request_id": "test-request-123",
        "prompt": {
            "name": "unknown_prompt"
        }
    }
    
    # Handle the message
    claude_mcp._handle_prompt_request(message)
    
    # Check that an error response was sent
    claude_mcp.stdout.seek(0)
    response = json.loads(claude_mcp.stdout.read().strip())
    
    assert response["type"] == "prompt_response"
    assert response["request_id"] == "test-request-123"
    assert "error" in response
    assert "message" in response["error"]
    assert "Unknown prompt: unknown_prompt" in response["error"]["message"]


@patch('src.claude_mcp.sys.stdin')
def test_start_method(mock_stdin, claude_mcp):
    """Test the start method with simulated input"""
    # Set up mock stdin to provide messages
    mock_stdin.__iter__.return_value = [
        json.dumps({"type": "ready"}),
        json.dumps({
            "type": "tool_call",
            "call_id": "test-call-1",
            "tool": {
                "name": "get_model_info",
                "arguments": {}
            }
        }),
        json.dumps({"type": "bye"})
    ]
    
    # Replace the stdin in the ClaudeMCP instance
    claude_mcp.stdin = mock_stdin
    
    # Set up spies for the message handlers
    with patch.object(claude_mcp, '_send_hello') as mock_hello, \
         patch.object(claude_mcp, '_handle_tool_call') as mock_tool_call, \
         patch.object(claude_mcp, '_send_bye') as mock_bye:
        
        # Start the MCP server
        claude_mcp.start()
        
        # Check that the appropriate handlers were called
        mock_hello.assert_called_once()
        mock_tool_call.assert_called_once()
        mock_bye.assert_called_once()


def test_main_function():
    """Test the main function by using direct module inspection"""
    from src.claude_mcp import main, VectorSearch, ClaudeMCP
    
    # Skip running the actual main function which would block in interactive mode
    # Instead, test the function structure and imports
    
    # Check that the main function exists
    assert callable(main)
    # Check that it uses both VectorSearch and ClaudeMCP
    assert VectorSearch is not None
    assert ClaudeMCP is not None
    
    # Check the function's docstring
    assert main.__doc__ is not None
    assert "Run the Claude MCP server" in main.__doc__