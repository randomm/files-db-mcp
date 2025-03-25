"""
Vector search engine for retrieving files by content similarity
"""

import logging
import os
import time
from typing import Any, Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor

from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer

logger = logging.getLogger("files-db-mcp.vector_search")


class VectorSearch:
    """
    Vector search engine using Qdrant as the backend
    """

    def __init__(
        self,
        host: str,
        port: int,
        embedding_model: str,
        quantization: bool = True,
        binary_embeddings: bool = False,
        collection_name: str = "files",
        model_config: Optional[Dict[str, Any]] = None,
    ):
        self.host = host
        self.port = port
        self.model_name = embedding_model
        self.quantization = quantization
        self.binary_embeddings = binary_embeddings
        self.collection_name = collection_name
        self.model_config = model_config or {}
        
        # Store normalize_embeddings setting to use during encoding
        # Default to True if not specified in model_config
        self.normalize_embeddings = self.model_config.get("normalize_embeddings", True)

        # Connect to Qdrant
        self.client = QdrantClient(host=host, port=port)

        # Initialize embedding model
        logger.info(f"Loading embedding model: {embedding_model}")
        self.model = self._load_embedding_model(embedding_model)
        self.vector_size = self.model.get_sentence_embedding_dimension()

        # Create collection if it doesn't exist
        self._initialize_collection()

    def _load_embedding_model(self, model_name: str) -> SentenceTransformer:
        """
        Load the embedding model with the specified configuration

        Args:
            model_name: The name or path of the embedding model

        Returns:
            The loaded SentenceTransformer model
        """
        # Apply model configuration if provided
        device = self.model_config.get("device", None)  # Get device from config or use default

        # Extract valid parameters for SentenceTransformer constructor
        # Only 'device' and 'cache_folder' are valid for the constructor
        valid_params = {}
        
        # Set a default cache folder to ensure models are persisted across restarts
        # This should be mounted as a volume in Docker
        if 'cache_folder' in self.model_config:
            valid_params['cache_folder'] = self.model_config['cache_folder']
        else:
            # Use the default HuggingFace cache location which we mount as a volume
            import os
            cache_dir = os.environ.get("HF_HOME") or os.path.join(os.path.expanduser("~"), ".cache", "huggingface", "hub")
            valid_params['cache_folder'] = cache_dir
        
        # Track progress for downloading model components
        try:
            # Try using the ProgressCallback from huggingface_hub (newer versions)
            from huggingface_hub import logging as hf_logging
            
            # Check if ProgressCallback exists in this version
            if hasattr(hf_logging, 'ProgressCallback'):
                # Create handler for tracking download progress
                class ProgressHandler(hf_logging.ProgressCallback):
                    def __init__(self):
                        super().__init__()
                        self.current_file = None
                        self.progress = {}
                        
                    def on_download(self, filename: str, chunk_size: int, chunk_index: int, total_size: int):
                        file_display_name = filename.split('/')[-1]
                        self.current_file = file_display_name
                        
                        if not total_size:
                            # If total size is unknown, just log each chunk
                            logger.info(f"Downloading {file_display_name}: chunk {chunk_index}")
                            return
                        
                        # Calculate progress percentage
                        downloaded = chunk_index * chunk_size
                        percentage = min(100, int(downloaded * 100 / total_size))
                        
                        # Update progress
                        if percentage % 10 == 0 and (file_display_name not in self.progress or self.progress[file_display_name] < percentage):
                            self.progress[file_display_name] = percentage
                            logger.info(f"Downloading {file_display_name}: {percentage}% ({downloaded//1024}KB / {total_size//1024}KB)")
                
                # Register progress handler
                progress_handler = ProgressHandler()
                hf_logging.callback_registry.register_callback(progress_handler)
                logger.info("Using progress callback for HuggingFace model downloads")
            else:
                logger.info("Progress callback not available in this huggingface-hub version")
        except (ImportError, AttributeError):
            logger.info("HuggingFace progress tracking not available, continuing without progress reporting")
        
        # Log start of model loading
        logger.info(f"Starting to load model: {model_name}")
        logger.info("Large models may take several minutes to download on first run")
        
        # Load model with appropriate configuration
        model = SentenceTransformer(
            model_name,
            device=device,
            **valid_params,
        )
        
        # Unregister progress handler after loading if it was registered
        try:
            if 'progress_handler' in locals() and hasattr(hf_logging, 'callback_registry'):
                hf_logging.callback_registry.unregister_callback(progress_handler)
        except Exception as e:
            logger.debug(f"Failed to unregister progress callback: {e}")
        
        # Log final message
        logger.info(f"Model {model_name} loaded successfully")
        
        return model

    def _initialize_collection(self):
        """Initialize vector collection"""
        try:
            collections = self.client.get_collections().collections
            collection_names = [c.name for c in collections]

            if self.collection_name not in collection_names:
                logger.info(f"Creating collection: {self.collection_name}")

                # Create vector collection
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(
                        size=self.vector_size,
                        distance=models.Distance.COSINE,
                    ),
                    # Add payload fields for filtering
                    optimizers_config=models.OptimizersConfigDiff(
                        indexing_threshold=0,  # Index immediately
                    ),
                )

                # Create indexes for faster filtering
                self.client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name="file_path",
                    field_schema=models.PayloadSchemaType.KEYWORD,
                )

                self.client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name="file_type",
                    field_schema=models.PayloadSchemaType.KEYWORD,
                )

                logger.info(f"Collection {self.collection_name} created successfully")
            else:
                logger.info(f"Collection {self.collection_name} already exists")
        except Exception as e:
            logger.error(f"Error initializing collection: {e!s}")
            raise

    def _generate_embedding(self, text: str, batch_size: int = 32) -> List[float]:
        """
        Generate embedding for text

        Args:
            text: The text to embed
            batch_size: Batch size for encoding (useful for longer texts)

        Returns:
            The embedding as a list of floats
        """
        # Apply prompt template if configured
        prompt_template = self.model_config.get("prompt_template", None)
        if prompt_template:
            text = prompt_template.format(text=text)

        # Use the normalize_embeddings setting we saved during model initialization
        embedding = self.model.encode(
            text,
            batch_size=batch_size,
            normalize_embeddings=self.normalize_embeddings,
            convert_to_tensor=False,
            show_progress_bar=False,
        )
        
        # Handle both numpy arrays and regular lists (for mocking in tests)
        if hasattr(embedding, 'tolist'):
            return embedding.tolist()
        else:
            # If it's already a list (e.g., in tests), return it as is
            return embedding

    def index_file(self, file_path: str, content: str, additional_metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Index file content in the vector database
        
        Args:
            file_path: Relative path to the file
            content: File content to index
            additional_metadata: Optional additional metadata to store with the document
            
        Returns:
            True if indexing was successful, False otherwise
        """
        try:
            # Get file extension for filtering
            _, file_extension = os.path.splitext(file_path)
            file_type = file_extension.lstrip(".").lower() if file_extension else "unknown"

            # Generate embedding for file content
            embedding = self._generate_embedding(content)

            # Create unique ID based on file path
            import hashlib

            point_id = hashlib.md5(file_path.encode()).hexdigest()
            
            # Create the payload with standard metadata
            payload = {
                "file_path": file_path,
                "file_type": file_type,
                "content": content,  # Store content for retrieval
                "indexed_at": time.time(),
            }
            
            # Add additional metadata if provided
            if additional_metadata:
                # Avoid overwriting standard fields
                for key, value in additional_metadata.items():
                    if key not in payload:
                        payload[key] = value
                    else:
                        # If it's a standard field, store it with a prefix
                        payload[f"meta_{key}"] = value

            # Upsert point into collection
            self.client.upsert(
                collection_name=self.collection_name,
                points=[
                    models.PointStruct(
                        id=point_id,
                        vector=embedding,
                        payload=payload,
                    )
                ],
            )

            logger.debug(f"Indexed file: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error indexing file {file_path}: {e!s}")
            return False
            
    def batch_index_files(self, file_paths: List[str], contents: List[str], additional_metadata_list: Optional[List[Dict[str, Any]]] = None) -> List[bool]:
        """
        Index multiple files at once in a batch operation for better performance
        
        Args:
            file_paths: List of relative paths to the files
            contents: List of file contents to index
            additional_metadata_list: Optional list of additional metadata to store with each document
            
        Returns:
            List of booleans indicating success for each file
        """
        if len(file_paths) != len(contents):
            logger.error("Mismatch between number of file paths and contents")
            return [False] * max(len(file_paths), len(contents))
            
        if additional_metadata_list and len(file_paths) != len(additional_metadata_list):
            logger.error("Mismatch between number of file paths and metadata entries")
            return [False] * len(file_paths)
            
        if not file_paths:
            return []
            
        try:
            # Prepare batch points
            points = []
            results = [False] * len(file_paths)
            
            # Generate embeddings for all files
            logger.debug(f"Generating embeddings for {len(file_paths)} files")
            
            # Create a function to prepare a point for upsert
            def prepare_point(idx):
                try:
                    file_path = file_paths[idx]
                    content = contents[idx]
                    
                    # Extract file type
                    _, file_extension = os.path.splitext(file_path)
                    file_type = file_extension.lstrip(".").lower() if file_extension else "unknown"
                    
                    # Create unique ID
                    import hashlib
                    point_id = hashlib.md5(file_path.encode()).hexdigest()
                    
                    # Generate embedding
                    embedding = self._generate_embedding(content)
                    
                    # Create payload
                    payload = {
                        "file_path": file_path,
                        "file_type": file_type,
                        "content": content,
                        "indexed_at": time.time(),
                    }
                    
                    # Add additional metadata if provided
                    if additional_metadata_list:
                        additional_metadata = additional_metadata_list[idx]
                        for key, value in additional_metadata.items():
                            if key not in payload:
                                payload[key] = value
                            else:
                                payload[f"meta_{key}"] = value
                    
                    # Create point
                    point = models.PointStruct(
                        id=point_id,
                        vector=embedding,
                        payload=payload,
                    )
                    
                    results[idx] = True
                    return point
                except Exception as e:
                    logger.error(f"Error preparing point for {file_paths[idx]}: {e!s}")
                    return None
            
            # Process all files in parallel with ThreadPoolExecutor
            with ThreadPoolExecutor(max_workers=min(8, len(file_paths))) as executor:
                # Map function to process all indexes
                point_results = list(executor.map(prepare_point, range(len(file_paths))))
                
                # Filter out None results
                points = [p for p in point_results if p is not None]
            
            # Only proceed if we have valid points
            if points:
                # Batch upsert all points at once
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=points,
                    wait=True
                )
                
                logger.debug(f"Batch indexed {len(points)} files successfully")
            else:
                logger.warning("No valid points to index in batch")
                
            return results
        except Exception as e:
            logger.error(f"Error in batch indexing: {e!s}")
            return [False] * len(file_paths)

    def delete_file(self, file_path: str) -> bool:
        """
        Delete file from vector database
        """
        try:
            # Create unique ID based on file path
            import hashlib

            point_id = hashlib.md5(file_path.encode()).hexdigest()

            # Delete point from collection
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.PointIdsList(
                    points=[point_id],
                ),
            )

            logger.debug(f"Deleted file: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error deleting file {file_path}: {e!s}")
            return False

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current embedding model

        Returns:
            Dictionary containing model information
        """
        return {
            "model_name": self.model_name,
            "vector_size": self.vector_size,
            "quantization": self.quantization,
            "binary_embeddings": self.binary_embeddings,
            "model_config": self.model_config,
            "collection_name": self.collection_name,
            "index_stats": {
                "total_points": self.client.count(collection_name=self.collection_name).count
            },
        }

    def change_model(self, new_model: str, model_config: Optional[Dict[str, Any]] = None) -> bool:
        """
        Change the embedding model

        Args:
            new_model: The name or path of the new embedding model
            model_config: Optional configuration for the new model

        Returns:
            True if model was changed successfully
        """
        try:
            logger.info(f"Changing embedding model from {self.model_name} to {new_model}")

            # Update model configuration
            if model_config is not None:
                self.model_config = model_config

            # Load new model
            self.model_name = new_model
            self.model = self._load_embedding_model(new_model)

            # Update vector size
            new_vector_size = self.model.get_sentence_embedding_dimension()

            # If vector size changed, we need to recreate the collection
            if new_vector_size != self.vector_size:
                logger.warning(
                    f"Vector size changed from {self.vector_size} to {new_vector_size}. "
                    f"Recreating collection {self.collection_name}"
                )
                # Delete existing collection
                self.client.delete_collection(collection_name=self.collection_name)
                self.vector_size = new_vector_size
                # Create new collection
                self._initialize_collection()
                logger.info(f"Collection {self.collection_name} recreated successfully")

            return True
        except Exception as e:
            logger.error(f"Error changing model: {e!s}")
            return False

    def search(
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
    ) -> List[Dict[str, Any]]:
        """
        Search for files by similarity to query with advanced filtering

        Args:
            query: Search query
            limit: Maximum number of results
            file_type: Filter by file type
            path_prefix: Filter by path prefix
            file_extensions: Filter by file extensions (e.g., ["py", "js"])
            modified_after: Filter by modification time (after timestamp)
            modified_before: Filter by modification time (before timestamp)
            exclude_paths: Exclude paths containing these strings
            custom_metadata: Custom metadata filters as key-value pairs
            threshold: Minimum similarity score threshold
            search_params: Additional search parameters for Qdrant

        Returns:
            List of search results
        """
        try:
            # Generate embedding for query
            query_embedding = self._generate_embedding(query)

            # Build filter
            filter_conditions = []

            # File type filter
            if file_type:
                filter_conditions.append(
                    models.FieldCondition(
                        key="file_type",
                        match=models.MatchValue(value=file_type),
                    )
                )

            # File extensions filter
            if file_extensions:
                filter_conditions.append(
                    models.FieldCondition(
                        key="file_type",
                        match=models.MatchAny(any=file_extensions),
                    )
                )

            # Path prefix filter
            if path_prefix:
                filter_conditions.append(
                    models.FieldCondition(
                        key="file_path",
                        match=models.MatchText(text=path_prefix),
                    )
                )

            # Modification time filters
            if modified_after:
                filter_conditions.append(
                    models.FieldCondition(
                        key="indexed_at",
                        range=models.Range(
                            gt=modified_after,
                        ),
                    )
                )

            if modified_before:
                filter_conditions.append(
                    models.FieldCondition(
                        key="indexed_at",
                        range=models.Range(
                            lt=modified_before,
                        ),
                    )
                )

            # Custom metadata filters
            if custom_metadata:
                for key, value in custom_metadata.items():
                    filter_conditions.append(
                        models.FieldCondition(
                            key=key,
                            match=models.MatchValue(value=value),
                        )
                    )

            # Create must conditions (AND)
            must_conditions = filter_conditions

            # Create must_not conditions (NOT)
            must_not_conditions = []

            # Exclude paths
            if exclude_paths:
                for exclude_path in exclude_paths:
                    must_not_conditions.append(
                        models.FieldCondition(
                            key="file_path",
                            match=models.MatchText(text=exclude_path),
                        )
                    )

            # Build search filter
            search_filter = None
            if must_conditions or must_not_conditions:
                search_filter = models.Filter(
                    must=must_conditions if must_conditions else None,
                    must_not=must_not_conditions if must_not_conditions else None,
                )

            # Apply additional search parameters if provided
            search_kwargs = {
                "collection_name": self.collection_name,
                "query_vector": query_embedding,
                "limit": limit,
                "query_filter": search_filter,
                "with_payload": True,
                "score_threshold": threshold,  # Only return results above threshold
            }

            # Add additional search parameters if provided
            if search_params:
                # Handle additional Qdrant search parameters
                if "hnsw_ef" in search_params:
                    search_kwargs["search_params"] = models.SearchParams(
                        hnsw_ef=search_params["hnsw_ef"]
                    )
                if search_params.get("exact"):
                    search_kwargs["search_params"] = models.SearchParams(exact=True)

            # Perform search
            results = self.client.search(**search_kwargs)

            # Format results
            formatted_results = []
            for res in results:
                formatted_results.append(
                    {
                        "file_path": res.payload.get("file_path"),
                        "file_type": res.payload.get("file_type"),
                        "content": res.payload.get("content"),
                        "score": res.score,
                        "metadata": {
                            k: v
                            for k, v in res.payload.items()
                            if k not in ["file_path", "file_type", "content"]
                        },
                    }
                )

            return formatted_results
        except Exception as e:
            logger.error(f"Error searching: {e!s}")
            return []
