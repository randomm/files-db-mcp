"""
Claude Code MCP integration for Files-DB-MCP

This module implements the Model Context Protocol (MCP) interface for Claude Code,
allowing direct integration between Claude's AI capabilities and the vector search system.
"""

import json
import logging
import subprocess
import sys
import os
from typing import Dict, Any, List, Optional
import argparse

from src.vector_search import VectorSearch

logger = logging.getLogger("files-db-mcp.claude_mcp")

# MCP message types
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

class ClaudeMCP:
    """
    MCP implementation for Claude Code integration with files-db-mcp
    """
    
    def __init__(self, vector_search: VectorSearch):
        """
        Initialize the Claude MCP interface
        
        Args:
            vector_search: The vector search engine
        """
        self.vector_search = vector_search
        self.stdin = sys.stdin
        self.stdout = sys.stdout
        self.name = "files-db-mcp"
        self.version = "0.1.0"
        
    def start(self):
        """Start the MCP server and handle messages"""
        try:
            # Send hello message
            self._send_hello()
            
            # Process incoming messages
            for line in self.stdin:
                if not line.strip():
                    continue
                    
                try:
                    message = json.loads(line)
                    message_type = message.get("type")
                    
                    if message_type == MESSAGE_TYPE_READY:
                        logger.info("MCP client is ready")
                    elif message_type == MESSAGE_TYPE_TOOL_CALL:
                        self._handle_tool_call(message)
                    elif message_type == MESSAGE_TYPE_RESOURCE_REQUEST:
                        self._handle_resource_request(message)
                    elif message_type == MESSAGE_TYPE_PROMPT_REQUEST:
                        self._handle_prompt_request(message)
                    elif message_type == MESSAGE_TYPE_BYE:
                        logger.info("MCP client is disconnecting")
                        break
                    else:
                        self._send_error(f"Unknown message type: {message_type}")
                        
                except json.JSONDecodeError:
                    self._send_error("Invalid JSON in message")
                except Exception as e:
                    self._send_error(f"Error processing message: {e}")
                    
        except KeyboardInterrupt:
            logger.info("MCP server was interrupted")
        except Exception as e:
            logger.error(f"MCP server error: {e}")
            self._send_error(f"Server error: {e}")
            
        # Send goodbye message
        self._send_bye()
        
    def _send_message(self, message: Dict[str, Any]):
        """Send a message to the client"""
        json_str = json.dumps(message)
        self.stdout.write(json_str + "\n")
        self.stdout.flush()
        
    def _send_hello(self):
        """Send hello message with server capabilities"""
        hello_message = {
            "type": MESSAGE_TYPE_HELLO,
            "server": {
                "name": self.name,
                "version": self.version
            },
            "capabilities": {
                "tools": {
                    "vector_search": {
                        "description": "Search for files in the codebase using vector similarity",
                        "parameters": {
                            "query": {
                                "type": "string",
                                "description": "The search query"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of results to return",
                                "default": 10
                            },
                            "file_type": {
                                "type": "string",
                                "description": "Optional file type filter",
                                "optional": True
                            },
                            "path_prefix": {
                                "type": "string", 
                                "description": "Filter by path prefix",
                                "optional": True
                            },
                            "file_extensions": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Filter by file extensions (e.g., ['py', 'js'])",
                                "optional": True
                            },
                            "threshold": {
                                "type": "number",
                                "description": "Minimum similarity score threshold",
                                "default": 0.6,
                                "optional": True
                            }
                        }
                    },
                    "get_file_content": {
                        "description": "Get the content of a specific file",
                        "parameters": {
                            "file_path": {
                                "type": "string",
                                "description": "Path to the file"
                            }
                        }
                    },
                    "get_model_info": {
                        "description": "Get information about the current embedding model",
                        "parameters": {}
                    }
                },
                "resources": {
                    "vector_search_info": {
                        "uri_template": "vector-search://{type}",
                        "description": "Get information about the vector search engine"
                    }
                },
                "prompts": {
                    "vector_search_help": {
                        "description": "Get help on how to use vector search"
                    }
                }
            }
        }
        self._send_message(hello_message)
        
    def _send_error(self, message: str):
        """Send an error message"""
        error_message = {
            "type": MESSAGE_TYPE_ERROR,
            "message": message
        }
        self._send_message(error_message)
        
    def _send_bye(self):
        """Send a goodbye message"""
        bye_message = {
            "type": MESSAGE_TYPE_BYE
        }
        self._send_message(bye_message)
        
    def _handle_tool_call(self, message: Dict[str, Any]):
        """Handle a tool call message"""
        call_id = message.get("call_id")
        tool = message.get("tool", {})
        name = tool.get("name")
        arguments = tool.get("arguments", {})
        
        try:
            if name == "vector_search":
                result = self._tool_vector_search(arguments)
            elif name == "get_file_content":
                result = self._tool_get_file_content(arguments)
            elif name == "get_model_info":
                result = self._tool_get_model_info(arguments)
            else:
                raise ValueError(f"Unknown tool: {name}")
                
            # Send tool result
            result_message = {
                "type": MESSAGE_TYPE_TOOL_RESULT,
                "call_id": call_id,
                "content": result
            }
            self._send_message(result_message)
            
        except Exception as e:
            # Send error result
            error_message = {
                "type": MESSAGE_TYPE_TOOL_RESULT,
                "call_id": call_id,
                "error": {
                    "message": str(e)
                }
            }
            self._send_message(error_message)
            
    def _handle_resource_request(self, message: Dict[str, Any]):
        """Handle a resource request message"""
        request_id = message.get("request_id")
        uri = message.get("uri", "")
        
        try:
            if uri.startswith("vector-search://"):
                resource_type = uri.replace("vector-search://", "")
                result = self._resource_vector_search_info(resource_type)
            else:
                raise ValueError(f"Unknown resource URI: {uri}")
                
            # Send resource response
            response_message = {
                "type": MESSAGE_TYPE_RESOURCE_RESPONSE,
                "request_id": request_id,
                "contents": result
            }
            self._send_message(response_message)
            
        except Exception as e:
            # Send error response
            error_message = {
                "type": MESSAGE_TYPE_RESOURCE_RESPONSE,
                "request_id": request_id,
                "error": {
                    "message": str(e)
                }
            }
            self._send_message(error_message)
            
    def _handle_prompt_request(self, message: Dict[str, Any]):
        """Handle a prompt request message"""
        request_id = message.get("request_id")
        prompt = message.get("prompt", {})
        name = prompt.get("name")
        
        try:
            if name == "vector_search_help":
                result = self._prompt_vector_search_help()
            else:
                raise ValueError(f"Unknown prompt: {name}")
                
            # Send prompt response
            response_message = {
                "type": MESSAGE_TYPE_PROMPT_RESPONSE,
                "request_id": request_id,
                "content": result
            }
            self._send_message(response_message)
            
        except Exception as e:
            # Send error response
            error_message = {
                "type": MESSAGE_TYPE_PROMPT_RESPONSE,
                "request_id": request_id,
                "error": {
                    "message": str(e)
                }
            }
            self._send_message(error_message)
            
    def _tool_vector_search(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Implement the vector_search tool
        
        Args:
            arguments: Tool arguments
            
        Returns:
            Search results in a format suitable for Claude Code
        """
        query = arguments.get("query")
        limit = arguments.get("limit", 10)
        file_type = arguments.get("file_type")
        path_prefix = arguments.get("path_prefix")
        file_extensions = arguments.get("file_extensions")
        threshold = arguments.get("threshold", 0.6)
        
        if not query:
            raise ValueError("Query is required")
            
        # Call the vector search engine
        results = self.vector_search.search(
            query=query,
            limit=limit,
            file_type=file_type,
            path_prefix=path_prefix,
            file_extensions=file_extensions,
            threshold=threshold
        )
        
        # Format results for Claude Code
        formatted_results = []
        for result in results:
            formatted_results.append({
                "file_path": result.get("file_path", ""),
                "score": result.get("score", 0),
                "snippet": result.get("snippet", ""),
                "metadata": {
                    "file_type": result.get("metadata", {}).get("file_type", ""),
                    "file_size": result.get("metadata", {}).get("file_size", 0),
                    "last_modified": result.get("metadata", {}).get("last_modified", 0)
                }
            })
            
        return [{
            "type": "text",
            "text": json.dumps(formatted_results, indent=2)
        }]
        
    def _tool_get_file_content(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Implement the get_file_content tool
        
        Args:
            arguments: Tool arguments
            
        Returns:
            File content in a format suitable for Claude Code
        """
        file_path = arguments.get("file_path")
        
        if not file_path:
            raise ValueError("File path is required")
            
        # Call the vector search engine to get file content
        result = self.vector_search.get_file_content(file_path)
        
        if not result.get("success", False):
            raise ValueError(result.get("error", f"Failed to get content for {file_path}"))
            
        return [{
            "type": "text",
            "text": result.get("content", "")
        }]
        
    def _tool_get_model_info(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Implement the get_model_info tool
        
        Args:
            arguments: Tool arguments
            
        Returns:
            Model information in a format suitable for Claude Code
        """
        # Get model info from vector search engine
        model_info = self.vector_search.get_model_info()
        
        return [{
            "type": "text",
            "text": json.dumps(model_info, indent=2)
        }]
        
    def _resource_vector_search_info(self, resource_type: str) -> List[Dict[str, Any]]:
        """
        Implement the vector_search_info resource
        
        Args:
            resource_type: Type of information to retrieve
            
        Returns:
            Resource content in a format suitable for Claude Code
        """
        if resource_type == "stats":
            # Get statistics about the vector search engine
            stats = {
                "total_files_indexed": self.vector_search.get_collection_stats().get("total_files", 0),
                "collection_name": self.vector_search.collection_name,
                "model_name": self.vector_search.model_name,
                "dimension": self.vector_search.dimension,
                "server_address": f"{self.vector_search.host}:{self.vector_search.port}"
            }
            
            return [{
                "uri": f"vector-search://stats",
                "text": json.dumps(stats, indent=2)
            }]
        else:
            raise ValueError(f"Unknown resource type: {resource_type}")
            
    def _prompt_vector_search_help(self) -> List[Dict[str, Any]]:
        """
        Implement the vector_search_help prompt
        
        Returns:
            Prompt content in a format suitable for Claude Code
        """
        help_text = """
# Vector Search Help

Files-DB-MCP provides semantic search over your codebase using vector embeddings.

## Basic Search

To find relevant files, use the `vector_search` tool:

```json
{
  "query": "database connection",
  "limit": 5
}
```

## Advanced Filtering

You can filter results by file type, path, or extensions:

```json
{
  "query": "http server",
  "file_extensions": ["py", "js"],
  "path_prefix": "src/",
  "threshold": 0.7
}
```

## Getting File Content

To retrieve the full content of a file:

```json
{
  "file_path": "src/database.py"
}
```

## Model Information

To get information about the current embedding model:

```json
{}
```

## Tips for Effective Searches

1. Be specific in your queries
2. Use domain-specific terminology
3. Try multiple search terms if needed
4. Filter by file types for better results
5. Adjust the threshold for broader/narrower results
"""
        
        return [{
            "type": "text",
            "text": help_text
        }]


def main():
    """Run the Claude MCP server as a standalone program"""
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()]
    )
    
    # Parse arguments
    parser = argparse.ArgumentParser(description="Files-DB-MCP Claude Code integration")
    parser.add_argument(
        "--host",
        type=str,
        default=os.environ.get("VECTOR_DB_HOST", "localhost"),
        help="Vector database host"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("VECTOR_DB_PORT", "6333")),
        help="Vector database port"
    )
    parser.add_argument(
        "--embedding-model",
        type=str,
        default=os.environ.get(
            "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
        ),
        help="Embedding model to use"
    )
    
    args = parser.parse_args()
    
    # Create vector search engine
    from src.vector_search import VectorSearch
    vector_search = VectorSearch(
        host=args.host,
        port=args.port,
        embedding_model=args.embedding_model
    )
    
    # Create and start MCP server
    mcp_server = ClaudeMCP(vector_search=vector_search)
    mcp_server.start()


if __name__ == "__main__":
    main()