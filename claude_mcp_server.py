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
        default=os.environ.get("VECTOR_DB_HOST", "localhost"),
        help="Vector database host (default: localhost)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("VECTOR_DB_PORT", "6333")),
        help="Vector database port (default: 6333)"
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
    logger.info(f"Vector DB Host: {args.host}")
    logger.info(f"Vector DB Port: {args.port}")
    logger.info(f"Embedding Model: {args.embedding_model}")
    logger.info(f"Log Level: {args.log_level}")
    
    try:
        # Import here to avoid module import issues
        from src.vector_search import VectorSearch
        from src.claude_mcp import ClaudeMCP
        
        # Create the vector search engine
        vector_search = VectorSearch(
            host=args.host,
            port=args.port,
            embedding_model=args.embedding_model
        )
        
        # Create and start the MCP server
        mcp_server = ClaudeMCP(vector_search=vector_search)
        mcp_server.start()
        
    except Exception as e:
        logger.error(f"Error starting MCP server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()