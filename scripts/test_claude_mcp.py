#!/usr/bin/env python3
"""
Test script for the Claude MCP integration

This script simulates a Claude MCP client to test the Files-DB-MCP integration
without needing an actual Claude instance. It sends a sequence of MCP messages
and displays the responses.
"""

import json
import subprocess
import sys
import threading
import time
import os
from typing import Dict, Any, List, Optional

# Constants for MCP message types
MESSAGE_TYPE_HELLO = "hello"
MESSAGE_TYPE_READY = "ready"
MESSAGE_TYPE_TOOL_CALL = "tool_call" 
MESSAGE_TYPE_TOOL_RESULT = "tool_result"
MESSAGE_TYPE_RESOURCE_REQUEST = "resource_request"
MESSAGE_TYPE_RESOURCE_RESPONSE = "resource_response"
MESSAGE_TYPE_PROMPT_REQUEST = "prompt_request"
MESSAGE_TYPE_PROMPT_RESPONSE = "prompt_response"
MESSAGE_TYPE_ERROR = "error"
MESSAGE_TYPE_BYE = "bye"

class TestMCPClient:
    """Test client for Claude MCP integration"""
    
    def __init__(self):
        """Initialize the test client"""
        self.process = None
        self.reader_thread = None
        self.stop_reader = False
        
    def start_mcp_server(self):
        """Start the MCP server process"""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(script_dir)
        cmd = [
            "python",
            os.path.join(root_dir, "claude_mcp_server.py"),
            "--host", "localhost",
            "--port", "6333",
            "--log-level", "DEBUG"
        ]
        
        print(f"Starting MCP server with command: {' '.join(cmd)}")
        self.process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1  # Line buffered
        )
        
        # Start reader thread
        self.reader_thread = threading.Thread(target=self._read_responses)
        self.reader_thread.daemon = True
        self.reader_thread.start()
        
        # Wait for server to initialize
        time.sleep(1)
        
    def stop_mcp_server(self):
        """Stop the MCP server process"""
        if self.process:
            self.stop_reader = True
            self.send_message({
                "type": MESSAGE_TYPE_BYE
            })
            time.sleep(1)  # Give server a moment to process bye message
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                
            self.reader_thread.join(timeout=1)
            print("MCP server stopped")
            
    def _read_responses(self):
        """Read and print responses from the MCP server"""
        while not self.stop_reader and self.process.stdout:
            line = self.process.stdout.readline()
            if not line:
                if self.process.poll() is not None:
                    break
                continue
                
            try:
                data = json.loads(line)
                self._handle_response(data)
            except json.JSONDecodeError:
                print(f"Error parsing JSON: {line}")
                
    def _handle_response(self, data: Dict[str, Any]):
        """Handle a response from the MCP server"""
        message_type = data.get("type", "unknown")
        
        if message_type == MESSAGE_TYPE_HELLO:
            print("\n=== SERVER HELLO ===")
            print(f"Server: {data.get('server', {}).get('name')} {data.get('server', {}).get('version')}")
            print("Capabilities:")
            tools = data.get("capabilities", {}).get("tools", {})
            resources = data.get("capabilities", {}).get("resources", {})
            prompts = data.get("capabilities", {}).get("prompts", {})
            
            print(f"- Tools: {', '.join(tools.keys())}")
            print(f"- Resources: {', '.join(resources.keys())}")
            print(f"- Prompts: {', '.join(prompts.keys())}")
            
            # Send ready message
            self.send_message({
                "type": MESSAGE_TYPE_READY,
                "client": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            })
            
        elif message_type == MESSAGE_TYPE_TOOL_RESULT:
            print(f"\n=== TOOL RESULT ===")
            call_id = data.get("call_id", "unknown")
            print(f"Call ID: {call_id}")
            
            if "error" in data:
                print(f"ERROR: {data['error'].get('message', 'Unknown error')}")
            else:
                content = data.get("content", [])
                for item in content:
                    if item.get("type") == "text":
                        print(f"RESULT:\n{item.get('text', '')}")
                    else:
                        print(f"RESULT (non-text): {item}")
                        
        elif message_type == MESSAGE_TYPE_RESOURCE_RESPONSE:
            print(f"\n=== RESOURCE RESPONSE ===")
            request_id = data.get("request_id", "unknown")
            print(f"Request ID: {request_id}")
            
            if "error" in data:
                print(f"ERROR: {data['error'].get('message', 'Unknown error')}")
            else:
                contents = data.get("contents", [])
                for content in contents:
                    print(f"URI: {content.get('uri', 'unknown')}")
                    print(f"CONTENT:\n{content.get('text', '')}")
                    
        elif message_type == MESSAGE_TYPE_PROMPT_RESPONSE:
            print(f"\n=== PROMPT RESPONSE ===")
            request_id = data.get("request_id", "unknown")
            print(f"Request ID: {request_id}")
            
            if "error" in data:
                print(f"ERROR: {data['error'].get('message', 'Unknown error')}")
            else:
                content = data.get("content", [])
                for item in content:
                    if item.get("type") == "text":
                        print(f"CONTENT:\n{item.get('text', '')}")
                    else:
                        print(f"CONTENT (non-text): {item}")
                        
        elif message_type == MESSAGE_TYPE_ERROR:
            print(f"\n=== ERROR ===")
            print(f"Error: {data.get('message', 'Unknown error')}")
            
        elif message_type == MESSAGE_TYPE_BYE:
            print("\n=== SERVER BYE ===")
            
        else:
            print(f"\n=== UNKNOWN MESSAGE TYPE: {message_type} ===")
            print(json.dumps(data, indent=2))
            
    def send_message(self, message: Dict[str, Any]):
        """Send a message to the MCP server"""
        if not self.process or not self.process.stdin:
            print("Error: MCP server process not running")
            return
            
        json_str = json.dumps(message)
        self.process.stdin.write(json_str + "\n")
        self.process.stdin.flush()
        
    def test_tool_call(self, tool_name: str, arguments: Dict[str, Any], call_id: str = "test-call-1"):
        """Test a tool call"""
        message = {
            "type": MESSAGE_TYPE_TOOL_CALL,
            "call_id": call_id,
            "tool": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        self.send_message(message)
        
    def test_resource_request(self, uri: str, request_id: str = "test-request-1"):
        """Test a resource request"""
        message = {
            "type": MESSAGE_TYPE_RESOURCE_REQUEST,
            "request_id": request_id,
            "uri": uri
        }
        self.send_message(message)
        
    def test_prompt_request(self, prompt_name: str, request_id: str = "test-prompt-1"):
        """Test a prompt request"""
        message = {
            "type": MESSAGE_TYPE_PROMPT_REQUEST,
            "request_id": request_id,
            "prompt": {
                "name": prompt_name
            }
        }
        self.send_message(message)
        
def main():
    """Main function to run the test"""
    client = TestMCPClient()
    
    try:
        # Start MCP server
        client.start_mcp_server()
        
        # Wait for hello and ready exchange
        time.sleep(2)
        
        # Test vector_search tool
        print("\nTesting vector_search tool...")
        client.test_tool_call(
            tool_name="vector_search",
            arguments={
                "query": "vector database",
                "limit": 5
            },
            call_id="search-1"
        )
        time.sleep(2)
        
        # Test get_file_content tool
        print("\nTesting get_file_content tool...")
        client.test_tool_call(
            tool_name="get_file_content",
            arguments={
                "file_path": "src/main.py"  # Path should exist in your codebase
            },
            call_id="content-1"
        )
        time.sleep(2)
        
        # Test get_model_info tool
        print("\nTesting get_model_info tool...")
        client.test_tool_call(
            tool_name="get_model_info",
            arguments={},
            call_id="model-info-1"
        )
        time.sleep(2)
        
        # Test resource request
        print("\nTesting resource request...")
        client.test_resource_request(
            uri="vector-search://stats",
            request_id="stats-1"
        )
        time.sleep(2)
        
        # Test prompt request
        print("\nTesting prompt request...")
        client.test_prompt_request(
            prompt_name="vector_search_help",
            request_id="help-1"
        )
        time.sleep(2)
        
        print("\nAll tests completed!")
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        
    finally:
        # Stop MCP server
        client.stop_mcp_server()
        
if __name__ == "__main__":
    main()