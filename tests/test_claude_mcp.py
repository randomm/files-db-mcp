"""
Tests for the Claude MCP integration
"""

import unittest
import json
import io
import sys
from unittest.mock import patch, MagicMock

# Import the module to test
from src.claude_mcp import ClaudeMCP, MESSAGE_TYPE_HELLO, MESSAGE_TYPE_TOOL_CALL

class TestClaudeMCP(unittest.TestCase):
    """Tests for the Claude MCP integration"""
    
    def setUp(self):
        """Set up the test environment"""
        # Create a mock for vector_search
        self.mock_vector_search = MagicMock()
        
        # Mock search results
        self.mock_vector_search.search.return_value = [
            {
                "file_path": "src/test.py",
                "score": 0.85,
                "snippet": "def test_function():\n    return True",
                "metadata": {
                    "file_type": "python",
                    "file_size": 1024,
                    "last_modified": 1616161616
                }
            }
        ]
        
        # Mock file content
        self.mock_vector_search.get_file_content.return_value = {
            "success": True,
            "file_path": "src/test.py",
            "content": "def test_function():\n    return True"
        }
        
        # Mock model info
        self.mock_vector_search.get_model_info.return_value = {
            "model_name": "sentence-transformers/all-MiniLM-L6-v2",
            "dimension": 384,
            "type": "sentence-transformer"
        }
        
        # Mock collection stats
        mock_stats = MagicMock()
        mock_stats.get.return_value = 10
        self.mock_vector_search.get_collection_stats.return_value = mock_stats
        
        # Set other properties
        self.mock_vector_search.collection_name = "test_collection"
        self.mock_vector_search.model_name = "sentence-transformers/all-MiniLM-L6-v2"
        self.mock_vector_search.dimension = 384
        self.mock_vector_search.host = "localhost"
        self.mock_vector_search.port = 6333
        
        # Create the ClaudeMCP instance with mock stdin/stdout
        self.mock_stdin = io.StringIO()
        self.mock_stdout = io.StringIO()
        
        # Create the MCP instance
        self.mcp = ClaudeMCP(vector_search=self.mock_vector_search)
        self.mcp.stdin = self.mock_stdin
        self.mcp.stdout = self.mock_stdout
        
    def test_send_hello(self):
        """Test sending the hello message"""
        # Call the method
        self.mcp._send_hello()
        
        # Get the output
        output = self.mock_stdout.getvalue()
        
        # Parse the JSON
        message = json.loads(output)
        
        # Check the message type
        self.assertEqual(message["type"], MESSAGE_TYPE_HELLO)
        
        # Check server info
        self.assertEqual(message["server"]["name"], "files-db-mcp")
        self.assertEqual(message["server"]["version"], "0.1.0")
        
        # Check capabilities
        self.assertIn("tools", message["capabilities"])
        self.assertIn("vector_search", message["capabilities"]["tools"])
        self.assertIn("get_file_content", message["capabilities"]["tools"])
        self.assertIn("get_model_info", message["capabilities"]["tools"])
        
    @patch('src.claude_mcp.ClaudeMCP._send_message')
    def test_vector_search_tool(self, mock_send_message):
        """Test the vector_search tool"""
        # Create tool call message
        tool_call = {
            "type": MESSAGE_TYPE_TOOL_CALL,
            "call_id": "test_call_id",
            "tool": {
                "name": "vector_search",
                "arguments": {
                    "query": "test query",
                    "limit": 5
                }
            }
        }
        
        # Call the method
        self.mcp._handle_tool_call(tool_call)
        
        # Check that vector_search was called
        self.mock_vector_search.search.assert_called_once_with(
            query="test query",
            limit=5,
            file_type=None,
            path_prefix=None,
            file_extensions=None,
            threshold=0.6
        )
        
        # Check that _send_message was called with the correct result
        mock_send_message.assert_called_once()
        args = mock_send_message.call_args[0][0]
        self.assertEqual(args["type"], "tool_result")
        self.assertEqual(args["call_id"], "test_call_id")
        
    @patch('src.claude_mcp.ClaudeMCP._send_message')
    def test_get_file_content_tool(self, mock_send_message):
        """Test the get_file_content tool"""
        # Create tool call message
        tool_call = {
            "type": MESSAGE_TYPE_TOOL_CALL,
            "call_id": "test_call_id",
            "tool": {
                "name": "get_file_content",
                "arguments": {
                    "file_path": "src/test.py"
                }
            }
        }
        
        # Call the method
        self.mcp._handle_tool_call(tool_call)
        
        # Check that get_file_content was called
        self.mock_vector_search.get_file_content.assert_called_once_with("src/test.py")
        
        # Check that _send_message was called with the correct result
        mock_send_message.assert_called_once()
        args = mock_send_message.call_args[0][0]
        self.assertEqual(args["type"], "tool_result")
        self.assertEqual(args["call_id"], "test_call_id")
        
    @patch('src.claude_mcp.ClaudeMCP._send_message')
    def test_get_model_info_tool(self, mock_send_message):
        """Test the get_model_info tool"""
        # Create tool call message
        tool_call = {
            "type": MESSAGE_TYPE_TOOL_CALL,
            "call_id": "test_call_id",
            "tool": {
                "name": "get_model_info",
                "arguments": {}
            }
        }
        
        # Call the method
        self.mcp._handle_tool_call(tool_call)
        
        # Check that get_model_info was called
        self.mock_vector_search.get_model_info.assert_called_once()
        
        # Check that _send_message was called with the correct result
        mock_send_message.assert_called_once()
        args = mock_send_message.call_args[0][0]
        self.assertEqual(args["type"], "tool_result")
        self.assertEqual(args["call_id"], "test_call_id")
        
if __name__ == "__main__":
    unittest.main()