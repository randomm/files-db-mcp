from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from src.vector_search import VectorSearch


@pytest.fixture
def mock_sentence_transformer():
    """Mock SentenceTransformer class"""
    with patch("src.vector_search.SentenceTransformer") as mock:
        # Set up mock
        encoder_instance = MagicMock()
        
        # Create mock for encode method that returns both a numpy array and handles tolist
        mock_encode_result = MagicMock(spec=np.ndarray)
        mock_encode_result.tolist.return_value = [0.1, 0.2, 0.3, 0.4]
        encoder_instance.encode.return_value = mock_encode_result
        
        # Set dimension
        encoder_instance.get_sentence_embedding_dimension.return_value = 4
        
        # Return the mock instance when SentenceTransformer is called
        mock.return_value = encoder_instance

        yield mock


@pytest.fixture
def mock_qdrant_client():
    """Mock QdrantClient class"""
    with patch("src.vector_search.QdrantClient") as mock:
        # Set up mock for collections
        client_instance = mock.return_value

        # Set up mock for get_collections
        collections_response = MagicMock()
        collections_response.collections = []
        client_instance.get_collections.return_value = collections_response

        # Set up mock for search
        search_result = [
            MagicMock(
                id="test_id",
                score=0.95,
                payload={
                    "file_path": "/test/file.py",
                    "file_type": "py",
                    "content": "test content",
                    "indexed_at": 1234567890,
                },
            )
        ]
        client_instance.search.return_value = search_result

        # Set up mock for count
        count_result = MagicMock(count=10)
        client_instance.count.return_value = count_result

        yield mock


def test_vector_search_initialization(mock_sentence_transformer, mock_qdrant_client):
    """Test VectorSearch initialization"""
    # Create a VectorSearch instance
    vs = VectorSearch(
        host="localhost",
        port=6333,
        embedding_model="test_model",
        quantization=True,
        binary_embeddings=False,
        collection_name="test_collection",
        model_config={"device": "cpu"},
    )

    # Check that the model was loaded with the correct parameters
    # SentenceTransformer should only be called with model name and device
    mock_sentence_transformer.assert_called_once_with("test_model", device="cpu")

    # Check that normalize_embeddings was properly extracted from model_config
    assert hasattr(vs, "normalize_embeddings")
    assert vs.normalize_embeddings is True  # Default value

    # Check that the client was created
    mock_qdrant_client.assert_called_once_with(host="localhost", port=6333)

    # Check that the collection was initialized
    vs.client.get_collections.assert_called_once()
    vs.client.create_collection.assert_called_once()
    
def test_vector_search_initialization_with_custom_settings(mock_sentence_transformer, mock_qdrant_client):
    """Test VectorSearch initialization with custom settings"""
    # Create a VectorSearch instance with custom model_config
    vs = VectorSearch(
        host="localhost",
        port=6333,
        embedding_model="test_model",
        model_config={
            "device": "cuda:0",
            "cache_folder": "/tmp/cache",
            "normalize_embeddings": False,
            "prompt_template": "Code: {text}",
            "invalid_param": "should_be_ignored"
        },
    )

    # Check that the model was loaded with ONLY the valid parameters
    # Only model_name, device, and cache_folder should be passed to the constructor
    mock_sentence_transformer.assert_called_once_with(
        "test_model", 
        device="cuda:0",
        cache_folder="/tmp/cache"
    )
    
    # Check that normalize_embeddings was properly extracted from model_config
    assert vs.normalize_embeddings is False
    
    # Test with normalize_embeddings explicitly included in model_config
    mock_sentence_transformer.reset_mock()
    
    vs2 = VectorSearch(
        host="localhost",
        port=6333,
        embedding_model="test_model",
        model_config={"normalize_embeddings": False},
    )
    
    # normalize_embeddings should NOT be passed to the constructor
    mock_sentence_transformer.assert_called_once_with("test_model", device=None)
    assert vs2.normalize_embeddings is False


def test_generate_embedding(mock_sentence_transformer, mock_qdrant_client):
    """Test generate embedding method"""
    # Create a VectorSearch instance
    vs = VectorSearch(
        host="localhost",
        port=6333,
        embedding_model="test_model",
        model_config={"prompt_template": "query: {text}", "normalize_embeddings": True},
    )

    # Generate an embedding
    embedding = vs._generate_embedding("test text")

    # Check that the prompt template was applied and normalize_embeddings was correctly passed
    vs.model.encode.assert_called_once_with(
        "query: test text",
        batch_size=32,
        normalize_embeddings=True,  # This should match the value in model_config
        convert_to_tensor=False,
        show_progress_bar=False,
    )

    # Check that the embedding was converted to a list
    assert isinstance(embedding, list)
    
    # Test with normalize_embeddings set to False
    vs.model.encode.reset_mock()
    vs.normalize_embeddings = False
    
    embedding = vs._generate_embedding("test text")
    
    # Check that normalize_embeddings=False was passed to encode
    vs.model.encode.assert_called_once_with(
        "query: test text",
        batch_size=32,
        normalize_embeddings=False,  # Should use instance variable
        convert_to_tensor=False,
        show_progress_bar=False,
    )


def test_index_file(mock_sentence_transformer, mock_qdrant_client):
    """Test index_file method"""
    # Create a VectorSearch instance
    vs = VectorSearch(host="localhost", port=6333, embedding_model="test_model")

    # Create a spy for _generate_embedding
    with patch.object(
        vs, "_generate_embedding", return_value=[0.1, 0.2, 0.3, 0.4]
    ) as mock_generate:
        # Index a file with no additional metadata
        result = vs.index_file("/test/file.py", "test content")

        # Check that _generate_embedding was called
        mock_generate.assert_called_once_with("test content")

        # Check that upsert was called
        vs.client.upsert.assert_called_once()

        # Check result
        assert result is True
        
        # Reset mocks
        mock_generate.reset_mock()
        vs.client.upsert.reset_mock()
        
        # Test with additional metadata
        additional_metadata = {
            "mtime": 12345.6789,
            "size": 1024,
            "hash": "test_hash_digest",
            "indexed_at": 9876543.21,
        }
        
        result = vs.index_file("/test/file2.py", "content with metadata", additional_metadata)
        
        # Check that _generate_embedding was called
        mock_generate.assert_called_once_with("content with metadata")
        
        # Check that upsert was called with the right parameters
        vs.client.upsert.assert_called_once()
        
        # Get the payload from the upsert call
        upsert_args = vs.client.upsert.call_args[1]
        points = upsert_args["points"]
        payload = points[0].payload
        
        # Verify metadata was included in payload
        assert payload["file_path"] == "/test/file2.py"
        assert payload["content"] == "content with metadata"
        assert payload["mtime"] == 12345.6789
        assert payload["size"] == 1024
        assert payload["hash"] == "test_hash_digest"
        
        # Check result
        assert result is True


def test_search(mock_sentence_transformer, mock_qdrant_client):
    """Test search method"""
    # Create a VectorSearch instance
    vs = VectorSearch(host="localhost", port=6333, embedding_model="test_model")

    # Create a spy for _generate_embedding
    with patch.object(
        vs, "_generate_embedding", return_value=[0.1, 0.2, 0.3, 0.4]
    ) as mock_generate:
        # Search
        results = vs.search(
            query="test query",
            limit=10,
            file_type="py",
            path_prefix="/test",
            search_params={"exact": True},
        )

        # Check that _generate_embedding was called
        mock_generate.assert_called_once_with("test query")

        # Check that search was called with the right parameters
        vs.client.search.assert_called_once()

        # Check results
        assert len(results) == 1
        assert results[0]["file_path"] == "/test/file.py"
        assert results[0]["score"] == 0.95
        assert "content" in results[0]
        assert "file_type" in results[0]


def test_change_model(mock_sentence_transformer, mock_qdrant_client):
    """Test change_model method"""
    # Create a VectorSearch instance
    vs = VectorSearch(host="localhost", port=6333, embedding_model="test_model")

    # Initial checks
    assert vs.model_name == "test_model"

    # Change model with same vector size
    result = vs.change_model("new_model")

    # Check that the model was changed
    assert result is True
    assert vs.model_name == "new_model"
    assert mock_sentence_transformer.call_count == 2  # Initial load + change

    # Change model with different vector size
    vs.model.get_sentence_embedding_dimension.return_value = 8  # Change vector size

    result = vs.change_model("different_size_model", {"quantization": "int8"})

    # Check that the collection was recreated
    assert result is True
    vs.client.delete_collection.assert_called_once()
    assert vs.client.create_collection.call_count == 2  # Initial creation + recreation
    assert vs.vector_size == 8


def test_get_model_info(mock_sentence_transformer, mock_qdrant_client):
    """Test get_model_info method"""
    # Create a VectorSearch instance
    vs = VectorSearch(
        host="localhost", port=6333, embedding_model="test_model", model_config={"device": "cpu"}
    )

    # Get model info
    info = vs.get_model_info()

    # Check info
    assert info["model_name"] == "test_model"
    assert info["vector_size"] == 4
    assert info["quantization"] is True
    assert info["binary_embeddings"] is False
    assert "device" in info["model_config"]
    assert info["model_config"]["device"] == "cpu"
    assert info["collection_name"] == "files"
    assert "index_stats" in info
    assert info["index_stats"]["total_points"] == 10
