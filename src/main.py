"""
Main entry point for the Files-DB-MCP service
"""

import argparse
import logging
import os
from typing import Any, Dict, Optional

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI

from src.file_processor import FileProcessor
from src.file_watcher import FileWatcher
from src.mcp_interface import MCPInterface
from src.sse_interface import SSEInterface
from src.vector_search import VectorSearch
from src.project_initializer import ProjectInitializer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

logger = logging.getLogger("files-db-mcp")

# Load environment variables
load_dotenv()


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Files-DB-MCP: Vector database for code files with MCP interface"
    )

    parser.add_argument(
        "--project-path",
        type=str,
        default=os.getcwd(),
        help="Path to the project directory to index (default: current directory)",
    )

    parser.add_argument(
        "--data-dir",
        type=str,
        default=os.path.join(os.getcwd(), ".files-db-mcp"),
        help="Directory to store data (default: .files-db-mcp in current directory)",
    )

    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)",
    )

    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to (default: 8000)",
    )

    parser.add_argument(
        "--ignore",
        type=str,
        nargs="+",
        default=[
            ".git",
            "node_modules",
            "__pycache__",
            "*.pyc",
            "*.pyo",
            ".DS_Store",
            ".idea",
            ".vscode",
        ],
        help="Patterns to ignore during indexing (default: common ignored files)",
    )

    parser.add_argument(
        "--embedding-model",
        type=str,
        default=None,
        help="Embedding model to use (overrides auto-detection if specified)",
    )

    parser.add_argument(
        "--model-config",
        type=str,
        default="{}",
        help="JSON string with embedding model configuration (default: {})",
    )

    parser.add_argument(
        "--disable-sse",
        action="store_true",
        help="Disable SSE interface",
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode",
    )
    
    parser.add_argument(
        "--force-reindex",
        action="store_true",
        help="Force a full re-index of all files (disable incremental indexing)",
    )
    
    parser.add_argument(
        "--disable-auto-config",
        action="store_true",
        help="Disable automatic project configuration detection",
    )

    return parser.parse_args()


def create_app(
    project_path: str,
    data_dir: str,
    ignore_patterns: list,
    embedding_model: Optional[str],
    model_config: Optional[Dict[str, Any]] = None,
    disable_sse: bool = False,
    force_reindex: bool = False,
    disable_auto_config: bool = False,
) -> FastAPI:
    """Create FastAPI application with all components"""
    # Create FastAPI app
    app = FastAPI(
        title="Files-DB-MCP",
        description="Vector database for code files with MCP interface",
        version="0.1.0",
    )
    
    # Initialize project with auto-detection if enabled
    if not disable_auto_config:
        logger.info("Auto-configuration enabled, detecting project settings...")
        initializer = ProjectInitializer(project_path, data_dir)
        config = initializer.initialize_project()
        
        # Use auto-detected values unless overridden by command line arguments
        if embedding_model is None:
            embedding_model = config["embedding_model"]
            logger.info(f"Using auto-detected embedding model: {embedding_model}")
        else:
            logger.info(f"Using command-line specified embedding model: {embedding_model}")
            
        # Merge model configs, with command line taking precedence
        auto_model_config = config["model_config"]
        if model_config:
            auto_model_config.update(model_config)
        model_config = auto_model_config
        
        # Combine ignore patterns, with command line patterns taking precedence
        auto_ignore_patterns = config["ignore_patterns"]
        # Only use auto-detected patterns if no command line patterns were specified explicitly
        if ignore_patterns == [
            ".git", "node_modules", "__pycache__", "*.pyc", 
            "*.pyo", ".DS_Store", ".idea", ".vscode"
        ]:
            ignore_patterns = auto_ignore_patterns
        
        logger.info(f"Project initialization complete. Detected type: {config['primary_project_type']}")
    else:
        # If auto-detection is disabled, use the default embedding model if none specified
        if embedding_model is None:
            embedding_model = "sentence-transformers/all-MiniLM-L6-v2"
            logger.info(f"Using default embedding model: {embedding_model}")

    # Create vector search engine with retries for containerized environments
    max_retries = 5
    retry_interval = 5  # seconds
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Connecting to vector database (attempt {attempt+1}/{max_retries})...")
            
            vector_db_host = os.getenv("VECTOR_DB_HOST", "localhost")
            vector_db_port = int(os.getenv("VECTOR_DB_PORT", "6333"))
            
            logger.info(f"Vector DB connection: {vector_db_host}:{vector_db_port}")
            
            vector_search = VectorSearch(
                host=vector_db_host,
                port=vector_db_port,
                embedding_model=embedding_model,
                model_config=model_config,
            )
            
            # Test connection by getting collections list
            vector_search.client.get_collections()
            logger.info("Successfully connected to vector database")
            break
        except Exception as e:
            logger.warning(f"Failed to connect to vector database: {e!s}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_interval} seconds...")
                import time
                time.sleep(retry_interval)
            else:
                logger.error("Failed to connect to vector database after all retries")
                raise

    # Create file processor
    file_processor = FileProcessor(
        vector_search=vector_search,
        project_path=project_path,
        ignore_patterns=ignore_patterns,
        data_dir=data_dir,
    )

    # Create MCP interface with file processor for reindexing control
    mcp_interface = MCPInterface(vector_search=vector_search, file_processor=file_processor)

    # Create file watcher
    file_watcher = FileWatcher(
        project_path=project_path,
        ignore_patterns=ignore_patterns,
        on_file_change=lambda event_type, file_path: file_processor.handle_file_change(event_type, file_path),
    )

    # Create SSE interface if enabled
    if not disable_sse:
        SSEInterface(
            app=app,
            vector_search=vector_search,
            file_processor=file_processor,
        )  # No need to store reference as it registers itself with the app

    # Register routes
    @app.get("/")
    async def root():
        return {
            "name": "Files-DB-MCP",
            "version": "0.1.0",
            "description": "Vector database for code files with MCP interface",
        }
        
    @app.get("/health")
    async def health():
        """Health check endpoint for container health monitoring"""
        # Check connection to vector DB
        from fastapi import HTTPException
        try:
            # Basic check to verify Qdrant is accessible
            vector_search.client.get_collections()
            
            # Get current embedding model info
            model_info = {
                "model_name": vector_search.model_name,
                "vector_size": vector_search.vector_size
            }
            
            # Extended health information
            status_info = {
                "status": "healthy",
                "vector_db": "connected",
                "indexed_files": file_processor.get_files_indexed(),
                "total_files": file_processor.get_total_files(),
                "indexing_progress": file_processor.get_indexing_progress(),
                "model_info": model_info,
                "is_indexing": file_processor.indexing_in_progress
            }
            
            # Add performance metrics if available
            if hasattr(file_processor, "last_batch_speed"):
                status_info["indexing_speed"] = {
                    "files_per_second": file_processor.last_batch_speed
                }
                
            return status_info
        except Exception as e:
            logger.error(f"Health check failed: {e!s}")
            raise HTTPException(
                status_code=500,
                detail={
                    "status": "unhealthy",
                    "error": f"{e!s}"
                }
            )

    @app.post("/mcp")
    async def handle_mcp_command(command: dict):
        """
        Handle MCP commands

        The command should be a JSON object with the following structure:
        {
            "function": "function_name",
            "parameters": { ... },
            "request_id": "optional_request_id"
        }
        """
        import json

        result = mcp_interface.handle_command(json.dumps(command))
        return json.loads(result)

    @app.on_event("startup")
    async def startup():
        """Initialize components on startup"""
        # Start file watcher in background
        file_watcher.start()

        # Start initial indexing in background
        # Use incremental indexing unless force_reindex is specified
        file_processor.schedule_indexing(incremental=not force_reindex)

    @app.on_event("shutdown")
    async def shutdown():
        """Clean up on shutdown"""
        # Stop file watcher
        file_watcher.stop()

    return app


def main():
    """Main entry point"""
    args = parse_args()

    # Configure logging level
    if args.debug:
        logging.getLogger("files-db-mcp").setLevel(logging.DEBUG)

    # Parse model config
    import json

    model_config = None
    if args.model_config and args.model_config != "{}":
        model_config = json.loads(args.model_config)

    # Create app
    app = create_app(
        project_path=args.project_path,
        data_dir=args.data_dir,
        ignore_patterns=args.ignore,
        embedding_model=args.embedding_model,
        model_config=model_config,
        disable_sse=args.disable_sse,
        force_reindex=args.force_reindex,
        disable_auto_config=args.disable_auto_config,
    )

    # Get port from environment variable if set, otherwise use args
    port = int(os.getenv("PORT", args.port))
    
    # Log startup information
    logger.info(f"Starting Files-DB-MCP on {args.host}:{port}")
    logger.info(f"Project path: {args.project_path}")
    logger.info(f"Data directory: {args.data_dir}")
    
    # Run app
    uvicorn.run(app, host=args.host, port=port)


if __name__ == "__main__":
    main()
