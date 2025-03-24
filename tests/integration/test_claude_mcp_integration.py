"""
Integration tests for Claude MCP implementation
"""

import json
import io
import threading
import time
from unittest.mock import MagicMock, patch, call

import pytest

from src.claude_mcp import ClaudeMCP


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


class MockIOStream:
    """Mock IO stream for testing bidirectional communication"""
    def __init__(self):
        self.input_buffer = io.StringIO()
        self.output_buffer = io.StringIO()
        self.closed = False
    
    def write(self, text):
        self.output_buffer.write(text)
        return len(text)
    
    def flush(self):
        pass
    
    def readline(self):
        if self.closed:
            return ""
        
        line = self.input_buffer.readline()
        if not line:
            # If no more lines, wait for more input or close
            time.sleep(0.1)
            if self.closed:
                return ""
            line = self.input_buffer.readline()
        return line
    
    def add_input(self, text):
        """Add text to the input buffer"""
        position = self.input_buffer.tell()
        self.input_buffer = io.StringIO(self.input_buffer.getvalue() + text)
        self.input_buffer.seek(position)
    
    def get_output(self):
        """Get the current output buffer content"""
        self.output_buffer.seek(0)
        return self.output_buffer.read()
    
    def clear_output(self):
        """Clear the output buffer"""
        self.output_buffer = io.StringIO()
    
    def __iter__(self):
        return self
    
    def __next__(self):
        line = self.readline()
        if line:
            return line
        raise StopIteration


@pytest.fixture
def mock_io_stream():
    """Create a mock IO stream for testing"""
    return MockIOStream()


@pytest.fixture
def claude_mcp_with_mock_io(mocked_vector_search, mock_io_stream):
    """Create a ClaudeMCP instance with mock IO streams"""
    mcp = ClaudeMCP(vector_search=mocked_vector_search)
    mcp.stdin = mock_io_stream
    mcp.stdout = mock_io_stream
    return mcp


def test_full_communication_flow():
    """Test the full communication flow between client and server without threading"""
    # Create a direct test setup
    vector_search_mock = MagicMock()
    mcp = ClaudeMCP(vector_search=vector_search_mock)
    
    # Mock all the necessary methods and inputs
    with patch.object(mcp, '_tool_vector_search') as mock_tool_search, \
         patch.object(mcp, '_resource_vector_search_info') as mock_resource_info, \
         patch.object(mcp, '_prompt_vector_search_help') as mock_prompt_help, \
         patch.object(mcp, '_send_message') as mock_send_message, \
         patch.object(mcp, 'stdin') as mock_stdin, \
         patch.object(mcp, '_send_hello') as mock_hello, \
         patch.object(mcp, '_send_bye') as mock_bye:
        
        # Set up return values
        mock_tool_search.return_value = [{"type": "text", "text": "test search result"}]
        mock_resource_info.return_value = [{"uri": "vector-search://stats", "text": "test stats"}]
        mock_prompt_help.return_value = [{"type": "text", "text": "help text"}]
        
        # Set up test messages input sequence
        mock_stdin.__iter__.return_value = [
            json.dumps({"type": "ready"}),
            # 1. Tool call for vector search
            json.dumps({
                "type": "tool_call",
                "call_id": "test-call-123",
                "tool": {
                    "name": "vector_search",
                    "arguments": {
                        "query": "test function",
                        "limit": 5
                    }
                }
            }),
            # 2. Resource request
            json.dumps({
                "type": "resource_request",
                "request_id": "test-request-123",
                "uri": "vector-search://stats"
            }),
            # 3. Prompt request
            json.dumps({
                "type": "prompt_request",
                "request_id": "test-prompt-123",
                "prompt": {
                    "name": "vector_search_help"
                }
            }),
            # 4. Bye message
            json.dumps({"type": "bye"})
        ]
        
        # Run the MCP server directly
        mcp.start()
        
        # Verify hello message was sent
        mock_hello.assert_called_once()
        
        # Verify tool call handling
        mock_tool_search.assert_called_once_with({
            "query": "test function",
            "limit": 5
        })
        
        # Verify resource request handling
        mock_resource_info.assert_called_once_with("stats")
        
        # Verify prompt request handling
        mock_prompt_help.assert_called_once()
        
        # Verify bye message was sent
        mock_bye.assert_called_once()
        
        # Verify all expected messages were sent
        expected_calls = [
            # Hello (handled by mock_hello)
            # Tool result
            call({
                "type": "tool_result",
                "call_id": "test-call-123",
                "content": [{"type": "text", "text": "test search result"}]
            }),
            # Resource response
            call({
                "type": "resource_response",
                "request_id": "test-request-123",
                "contents": [{"uri": "vector-search://stats", "text": "test stats"}]
            }),
            # Prompt response
            call({
                "type": "prompt_response",
                "request_id": "test-prompt-123",
                "content": [{"type": "text", "text": "help text"}]
            }),
            # Bye (handled by mock_bye)
        ]
        
        # Verify that these calls were made (not necessarily in this order)
        for expected_call in expected_calls:
            assert expected_call in mock_send_message.call_args_list


def test_error_handling():
    """Test error handling in the MCP flow"""
    # Create direct test with mocks
    vector_search_mock = MagicMock()
    mcp = ClaudeMCP(vector_search=vector_search_mock)
    
    # Test JSON decode error handling
    with patch.object(mcp, '_send_error') as mock_send_error, \
         patch.object(mcp, '_send_message') as mock_send_message, \
         patch.object(mcp, 'stdin') as mock_stdin, \
         patch.object(mcp, '_send_hello') as mock_hello, \
         patch.object(mcp, '_send_bye') as mock_bye:
        
        # Test handling invalid JSON
        mock_stdin.__iter__.return_value = [
            "This is not valid JSON\n",
            json.dumps({"type": "bye"})
        ]
        
        # Run the MCP server directly (no threading)
        mcp.start()
        
        # Verify error was sent for invalid JSON
        mock_send_error.assert_any_call("Invalid JSON in message")
    
    # Test unknown tool handling
    with patch.object(mcp, '_handle_tool_call', wraps=mcp._handle_tool_call) as mock_tool_call, \
         patch.object(mcp, '_send_message') as mock_send_message, \
         patch.object(mcp, 'stdin') as mock_stdin, \
         patch.object(mcp, '_send_hello') as mock_hello, \
         patch.object(mcp, '_send_bye') as mock_bye:
        
        # Setup test message
        mock_stdin.__iter__.return_value = [
            json.dumps({
                "type": "tool_call",
                "call_id": "test-error-1",
                "tool": {
                    "name": "unknown_tool",
                    "arguments": {}
                }
            }),
            json.dumps({"type": "bye"})
        ]
        
        # Run the MCP server
        mcp.start()
        
        # Verify the tool call handler was called once
        mock_tool_call.assert_called_once()
        
        # Verify error message was sent
        mock_send_message.assert_any_call({
            "type": "tool_result",
            "call_id": "test-error-1",
            "error": {
                "message": "Unknown tool: unknown_tool"
            }
        })


def test_message_processing_order():
    """Test processing multiple messages in sequence"""
    # Create a direct test instead of threading
    vector_search_mock = MagicMock()
    mcp = ClaudeMCP(vector_search=vector_search_mock)
    
    # Mock the handlers directly
    with patch.object(mcp, '_handle_tool_call') as mock_tool_call, \
         patch.object(mcp, '_handle_resource_request') as mock_resource_request, \
         patch.object(mcp, '_handle_prompt_request') as mock_prompt_request, \
         patch.object(mcp, '_send_hello') as mock_hello, \
         patch.object(mcp, '_send_bye') as mock_bye, \
         patch.object(mcp, '_send_message') as mock_send_message, \
         patch.object(mcp, 'stdin') as mock_stdin:
        
        # Set up stdin to provide test messages
        mock_stdin.__iter__.return_value = [
            json.dumps({"type": "ready"}),
            json.dumps({
                "type": "tool_call",
                "call_id": "call-1",
                "tool": {"name": "get_model_info", "arguments": {}}
            }),
            json.dumps({
                "type": "resource_request",
                "request_id": "req-1",
                "uri": "vector-search://stats"
            }),
            json.dumps({
                "type": "prompt_request",
                "request_id": "prompt-1",
                "prompt": {"name": "vector_search_help"}
            }),
            json.dumps({"type": "bye"})
        ]
        
        # Run the MCP server directly (no threading)
        mcp.start()
        
        # Check that all methods were called
        mock_hello.assert_called_once()
        mock_tool_call.assert_called_once()
        mock_resource_request.assert_called_once()
        mock_prompt_request.assert_called_once()
        mock_bye.assert_called_once()