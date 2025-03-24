#!/usr/bin/env python3
"""
A standalone script to run the Files-DB-MCP Claude MCP server

This script can be used directly in Claude Desktop or Claude Code CLI configurations.
"""

import os
import sys
import logging
import argparse

# Set up logging to file
log_dir = os.path.expanduser("~/.files-db-mcp")
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(log_dir, "claude_mcp.log")),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("files-db-mcp.claude_mcp_server")

def main():
    """Run the Claude MCP server"""
    parser = argparse.ArgumentParser(description="Files-DB-MCP Claude MCP Server")
    parser.add_argument(
        "--host",
        type=str,
        default=os.environ.get("MCP_HOST", "localhost"),
        help="MCP interface host (default: localhost)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("MCP_PORT", "3000")),
        help="MCP interface port (default: 3000)"
    )
    parser.add_argument(
        "--embedding-model",
        type=str,
        default=os.environ.get(
            "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
        ),
        help="Embedding model to use (default: sentence-transformers/all-MiniLM-L6-v2)"
    )
    parser.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default=os.environ.get("LOG_LEVEL", "INFO"),
        help="Logging level (default: INFO)"
    )
    
    args = parser.parse_args()
    
    # Set log level
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    logger.info(f"Starting Files-DB-MCP Claude MCP Server with the following settings:")
    logger.info(f"MCP Interface Host: {args.host}")
    logger.info(f"MCP Interface Port: {args.port}")
    logger.info(f"Log Level: {args.log_level}")
    
    try:
        # Import here to avoid module import issues
        import requests
        from src.claude_mcp import ClaudeMCP
        
        # Create a class to handle communication with MCP interface
        class MCPInterface:
            def __init__(self, host, port):
                self.base_url = f"http://{host}:{port}"
                
            def search(self, query, limit=10, file_type=None, path_prefix=None, file_extensions=None, threshold=0.6):
                """Search via the MCP interface"""
                try:
                    response = requests.post(
                        f"{self.base_url}/mcp",
                        json={
                            "function": "vector_search",
                            "parameters": {
                                "query": query,
                                "limit": limit,
                                "file_type": file_type,
                                "path_prefix": path_prefix,
                                "file_extensions": file_extensions,
                                "threshold": threshold
                            }
                        }
                    )
                    response.raise_for_status()
                    return response.json()
                except requests.RequestException as e:
                    logger.error(f"Error connecting to MCP interface: {e}")
                    raise ConnectionError(f"Failed to connect to MCP interface: {e}")
                    
            def get_file_content(self, file_path):
                """Get file content via the MCP interface"""
                try:
                    response = requests.post(
                        f"{self.base_url}/mcp",
                        json={
                            "function": "get_file_content",
                            "parameters": {
                                "file_path": file_path
                            }
                        }
                    )
                    response.raise_for_status()
                    return response.json()
                except requests.RequestException as e:
                    logger.error(f"Error connecting to MCP interface: {e}")
                    raise ConnectionError(f"Failed to connect to MCP interface: {e}")
                    
            def get_model_info(self):
                """Get model info via the MCP interface"""
                try:
                    response = requests.post(
                        f"{self.base_url}/mcp",
                        json={
                            "function": "get_model_info",
                            "parameters": {}
                        }
                    )
                    response.raise_for_status()
                    return response.json()
                except requests.RequestException as e:
                    logger.error(f"Error connecting to MCP interface: {e}")
                    raise ConnectionError(f"Failed to connect to MCP interface: {e}")
                    
            def get_collection_stats(self):
                """Get collection stats via the health endpoint"""
                try:
                    response = requests.get(f"{self.base_url}/health")
                    response.raise_for_status()
                    data = response.json()
                    return {
                        "total_files": data.get("indexed_files", 0)
                    }
                except requests.RequestException as e:
                    logger.error(f"Error connecting to MCP interface health endpoint: {e}")
                    raise ConnectionError(f"Failed to connect to MCP interface: {e}")
        
        # Check if MCP interface is available
        try:
            logger.info(f"Checking MCP interface at {args.host}:{args.port}")
            response = requests.get(f"http://{args.host}:{args.port}/health")
            response.raise_for_status()
            logger.info(f"Successfully connected to MCP interface")
        except requests.RequestException as e:
            logger.error(f"Failed to connect to MCP interface: {e}")
            logger.error(f"Make sure Files-DB-MCP is running and accessible at {args.host}:{args.port}")
            sys.exit(1)
            
        # Create MCP interface wrapper
        mcp_interface = MCPInterface(args.host, args.port)
        
        # Create and start the MCP server
        mcp_server = ClaudeMCP(vector_search=mcp_interface)
        mcp_server.start()
        
    except Exception as e:
        logger.error(f"Error starting MCP server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()