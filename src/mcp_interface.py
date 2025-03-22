"""
MCP (Message Control Protocol) interface for communication with client tools
"""

import json
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger("files-db-mcp.mcp_interface")


class MCPInterface:
    """
    Implements the Message Control Protocol for communication with clients
    """

    def __init__(self, vector_search):
        self.vector_search = vector_search
        self.functions = self._register_functions()

    def _register_functions(self) -> Dict[str, callable]:
        """Register available MCP functions"""
        return {
            "search_files": self.search_files,
            "get_file_content": self.get_file_content,
            "get_model_info": self.get_model_info,
            "change_model": self.change_model,
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
