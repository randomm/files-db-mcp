"""
MCP (Message Control Protocol) interface for communication with client tools
"""

import json
import logging
import os
from typing import Any, Dict, List, Optional
from pathlib import Path

logger = logging.getLogger("files-db-mcp.mcp_interface")


class MCPInterface:
    """
    Implements the Message Control Protocol for communication with clients
    """

    def __init__(self, vector_search, file_processor=None):
        self.vector_search = vector_search
        self.file_processor = file_processor  # Add reference to file processor
        self.functions = self._register_functions()
        self.project_path = Path(getattr(file_processor, 'project_path', os.getcwd()))
        self.data_dir = Path(getattr(file_processor, 'data_dir', Path(os.getcwd()) / '.files-db-mcp'))

    def _register_functions(self) -> Dict[str, callable]:
        """Register available MCP functions"""
        return {
            "search_files": self.search_files,
            "get_file_content": self.get_file_content,
            "get_model_info": self.get_model_info,
            "change_model": self.change_model,
            "trigger_reindex": self.trigger_reindex,
            "get_indexing_status": self.get_indexing_status,
            "get_project_config": self.get_project_config,
            "detect_project_type": self.detect_project_type,
            "update_project_config": self.update_project_config,
        }

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current embedding model

        Returns:
            Model information
        """
        try:
            model_info = self.vector_search.get_model_info()
            return {"success": True, "model_info": model_info}
        except Exception as e:
            logger.error(f"Error in get_model_info: {e!s}")
            return {"success": False, "error": f"{e}"}

    def change_model(
        self, model_name: str, model_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Change the embedding model

        Args:
            model_name: The name or path of the new embedding model
            model_config: Optional configuration for the new model

        Returns:
            Success status and model information
        """
        try:
            success = self.vector_search.change_model(model_name, model_config)
            if success:
                model_info = self.vector_search.get_model_info()
                return {
                    "success": True,
                    "message": f"Model changed to {model_name}",
                    "model_info": model_info,
                }
            else:
                return {"success": False, "error": f"Failed to change model to {model_name}"}
        except Exception as e:
            logger.error(f"Error in change_model: {e!s}")
            return {"success": False, "error": f"{e}"}

    def search_files(
        self,
        query: str,
        limit: int = 10,
        file_type: Optional[str] = None,
        path_prefix: Optional[str] = None,
        file_extensions: Optional[List[str]] = None,
        modified_after: Optional[float] = None,
        modified_before: Optional[float] = None,
        exclude_paths: Optional[List[str]] = None,
        custom_metadata: Optional[Dict[str, Any]] = None,
        threshold: float = 0.6,
        search_params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Search for files by content similarity with advanced filtering

        Args:
            query: The search query
            limit: Maximum number of results to return
            file_type: Optional file type filter
            path_prefix: Filter by path prefix
            file_extensions: Filter by file extensions (e.g., ["py", "js"])
            modified_after: Filter by modification time (after timestamp)
            modified_before: Filter by modification time (before timestamp)
            exclude_paths: Exclude paths containing these strings
            custom_metadata: Custom metadata filters as key-value pairs
            threshold: Minimum similarity score threshold

        Returns:
            Search results
        """
        try:
            results = self.vector_search.search(
                query=query,
                limit=limit,
                file_type=file_type,
                path_prefix=path_prefix,
                file_extensions=file_extensions,
                modified_after=modified_after,
                modified_before=modified_before,
                exclude_paths=exclude_paths,
                custom_metadata=custom_metadata,
                threshold=threshold,
                search_params=search_params,
            )

            return {
                "success": True,
                "results": results,
                "count": len(results),
                "filters": {
                    "file_type": file_type,
                    "path_prefix": path_prefix,
                    "file_extensions": file_extensions,
                    "modified_after": modified_after,
                    "modified_before": modified_before,
                    "exclude_paths": exclude_paths,
                    "custom_metadata": custom_metadata,
                    "threshold": threshold,
                },
            }
        except Exception as e:
            logger.error(f"Error in search_files: {e!s}")
            return {
                "success": False,
                "error": f"{e}",
            }

    def trigger_reindex(self, incremental: bool = True) -> Dict[str, Any]:
        """
        Trigger a reindexing of files
        
        Args:
            incremental: Whether to use incremental indexing (default: True)
            
        Returns:
            Status of the operation
        """
        try:
            if not self.file_processor:
                return {
                    "success": False,
                    "error": "File processor not available",
                }
                
            # Check if indexing is already in progress
            if self.file_processor.is_indexing_complete():
                # If indexing is not in progress, start a new indexing process
                self.file_processor.schedule_indexing(incremental=incremental)
                return {
                    "success": True,
                    "message": f"Started {'incremental' if incremental else 'full'} reindexing",
                }
            else:
                return {
                    "success": False,
                    "error": "Indexing already in progress",
                    "progress": self.file_processor.get_indexing_progress(),
                }
        except Exception as e:
            logger.error(f"Error in trigger_reindex: {e!s}")
            return {
                "success": False, 
                "error": f"{e}"
            }
            
    def get_indexing_status(self) -> Dict[str, Any]:
        """
        Get current indexing status
        
        Returns:
            Indexing status information
        """
        try:
            if not self.file_processor:
                return {
                    "success": False,
                    "error": "File processor not available",
                }
                
            return {
                "success": True,
                "is_complete": self.file_processor.is_indexing_complete(),
                "progress": self.file_processor.get_indexing_progress(),
                "files_indexed": self.file_processor.get_files_indexed(),
                "total_files": self.file_processor.get_total_files(),
            }
        except Exception as e:
            logger.error(f"Error in get_indexing_status: {e!s}")
            return {
                "success": False,
                "error": f"{e}",
            }
            
    def get_file_content(self, file_path: str) -> Dict[str, Any]:
        """
        Get the content of a specific file

        Args:
            file_path: Path to the file

        Returns:
            File content
        """
        try:
            # Search for exact file path
            from qdrant_client.http import models

            results = self.vector_search.client.scroll(
                collection_name=self.vector_search.collection_name,
                scroll_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="file_path",
                            match=models.MatchValue(value=file_path),
                        )
                    ]
                ),
                limit=1,
                with_payload=True,
            )

            if not results.points:
                return {
                    "success": False,
                    "error": f"File not found: {file_path}",
                }

            return {
                "success": True,
                "file_path": file_path,
                "content": results.points[0].payload.get("content", ""),
            }
        except Exception as e:
            logger.error(f"Error in get_file_content: {e!s}")
            return {
                "success": False,
                "error": f"{e}",
            }

    def handle_command(self, command_str: str) -> str:
        """
        Handle MCP command from stdin

        Args:
            command_str: The command string in JSON format

        Returns:
            Response in JSON format
        """
        try:
            # Parse command
            command = json.loads(command_str)

            # Extract function name and parameters
            function_name = command.get("function")
            parameters = command.get("parameters", {})
            request_id = command.get("request_id")

            if not function_name:
                return json.dumps(
                    {
                        "success": False,
                        "error": "Missing function name",
                        "request_id": request_id,
                    }
                )

            # Check if function exists
            if function_name not in self.functions:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Unknown function: {function_name}",
                        "request_id": request_id,
                    }
                )

            # Call function
            result = self.functions[function_name](**parameters)

            # Add request ID to response
            if request_id:
                result["request_id"] = request_id

            return json.dumps(result)
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON: {command_str}")
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid JSON format",
                }
            )
        except Exception as e:
            logger.error(f"Error handling command: {e!s}")
            return json.dumps(
                {
                    "success": False,
                    "error": f"{e}",
                }
            )
    
    def get_project_config(self) -> Dict[str, Any]:
        """
        Get current project configuration
        
        Returns:
            Project configuration information
        """
        try:
            from src.project_initializer import ProjectInitializer
            
            # Initialize project initializer with current paths
            initializer = ProjectInitializer(
                project_path=self.project_path,
                data_dir=self.data_dir
            )
            
            # Load existing configuration if available
            config = initializer.load_config()
            
            if not config:
                return {
                    "success": False,
                    "error": "No project configuration found",
                    "message": "Run detect_project_type to create a configuration"
                }
                
            return {
                "success": True,
                "config": config
            }
        except Exception as e:
            logger.error(f"Error in get_project_config: {e!s}")
            return {
                "success": False,
                "error": f"{e}",
            }
    
    def detect_project_type(self, force_redetect: bool = False) -> Dict[str, Any]:
        """
        Detect project type and generate configuration
        
        Args:
            force_redetect: Whether to force redetection even if configuration exists
            
        Returns:
            Project type detection results
        """
        try:
            from src.project_initializer import ProjectInitializer
            
            # Initialize project initializer with current paths
            initializer = ProjectInitializer(
                project_path=self.project_path,
                data_dir=self.data_dir
            )
            
            # Check if configuration already exists
            config_file = self.data_dir / "config.json"
            if config_file.exists() and not force_redetect:
                config = initializer.load_config()
                return {
                    "success": True,
                    "message": "Using existing configuration",
                    "config": config,
                }
            
            # Run project initialization with auto-detection
            config = initializer.initialize_project()
            
            return {
                "success": True,
                "message": "Project type detection completed",
                "detected_types": config["project_types"],
                "primary_type": config["primary_project_type"],
                "embedding_model": config["embedding_model"],
                "ignore_patterns": config["ignore_patterns"],
                "config": initializer.load_config(),  # Load the saved configuration
            }
        except Exception as e:
            logger.error(f"Error in detect_project_type: {e!s}")
            return {
                "success": False,
                "error": f"{e}",
            }
    
    def update_project_config(
        self, 
        embedding_model: Optional[str] = None,
        model_config: Optional[Dict[str, Any]] = None,
        custom_ignore_patterns: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Update project configuration
        
        Args:
            embedding_model: Optional new embedding model to use
            model_config: Optional new model configuration
            custom_ignore_patterns: Optional custom ignore patterns to add
            
        Returns:
            Updated configuration
        """
        try:
            from src.project_initializer import ProjectInitializer
            
            # Initialize project initializer with current paths
            initializer = ProjectInitializer(
                project_path=self.project_path,
                data_dir=self.data_dir
            )
            
            # Load existing configuration
            config = initializer.load_config()
            if not config:
                return {
                    "success": False,
                    "error": "No configuration found to update",
                    "message": "Run detect_project_type first"
                }
            
            # Update configuration
            if embedding_model:
                config["embedding_model"] = embedding_model
                initializer.embedding_model = embedding_model
            
            if model_config:
                if "model_config" not in config:
                    config["model_config"] = {}
                config["model_config"].update(model_config)
                initializer.model_config = config["model_config"]
            
            if custom_ignore_patterns:
                if "custom_ignore_patterns" not in config:
                    config["custom_ignore_patterns"] = []
                # Add new patterns, avoiding duplicates
                existing_patterns = set(config["custom_ignore_patterns"])
                for pattern in custom_ignore_patterns:
                    if pattern not in existing_patterns:
                        config["custom_ignore_patterns"].append(pattern)
                initializer.custom_ignore_patterns = config["custom_ignore_patterns"]
            
            # Save updated configuration
            config_file = self.data_dir / "config.json"
            with open(config_file, "w") as f:
                json.dump(config, f, indent=2)
            
            # Restart the indexing with the new configuration if embedding model changed
            changed_embedding = embedding_model is not None
            changed_model_config = model_config is not None
            
            if (changed_embedding or changed_model_config) and self.vector_search:
                # Get the current model from config
                current_model = config.get("embedding_model", initializer.embedding_model)
                current_config = config.get("model_config", initializer.model_config)
                
                # Change the model
                self.vector_search.change_model(current_model, current_config)
                
                # Trigger reindexing if model changed
                if self.file_processor:
                    self.file_processor.schedule_indexing(incremental=False)
                    logger.info(f"Triggered reindexing with new embedding model: {current_model}")
            
            return {
                "success": True,
                "message": "Configuration updated successfully",
                "config": config,
                "reindexing_started": changed_embedding or changed_model_config,
            }
        except Exception as e:
            logger.error(f"Error in update_project_config: {e!s}")
            return {
                "success": False,
                "error": f"{e}",
            }
