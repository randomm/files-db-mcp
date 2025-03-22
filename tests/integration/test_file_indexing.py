"""
Integration tests for the file indexing process
"""

from unittest.mock import MagicMock, patch

import pytest

from src.file_processor import FileProcessor
from src.file_watcher import FileWatcher
from src.vector_search import VectorSearch


@pytest.mark.integration
@patch("src.vector_search.QdrantClient")
@patch("src.vector_search.SentenceTransformer")
def test_file_indexing_flow(mock_transformer, mock_qdrant, sample_project_dir):
    """Test the complete file indexing flow"""
    # Setup mocks
    mock_model = MagicMock()
    mock_model.encode.return_value = [0.1, 0.2, 0.3, 0.4, 0.5]
    mock_model.get_sentence_embedding_dimension.return_value = 5
    mock_transformer.return_value = mock_model

    mock_client = MagicMock()
    mock_qdrant.return_value = mock_client

    # Create vector search engine
    vector_search = VectorSearch(
        host="localhost", port=6333, embedding_model="test-model", collection_name="test-collection"
    )

    # Create file processor
    file_processor = FileProcessor(
        vector_search=vector_search,
        project_path=str(sample_project_dir),
        ignore_patterns=[".git", "*.pyc"],
        data_dir=str(sample_project_dir / "data"),
    )

    # Run indexing process
    file_processor.index_files()

    # Verify results
    assert file_processor.is_indexing_complete() is True
    assert file_processor.get_total_files() > 0
    assert file_processor.get_files_indexed() > 0
    assert file_processor.get_indexing_progress() == 100.0

    # Verify vector search calls
    assert mock_client.create_collection.called
    assert mock_model.encode.called
    assert mock_client.upsert.called


@pytest.mark.integration
@patch("src.vector_search.QdrantClient")
@patch("src.vector_search.SentenceTransformer")
@patch("src.file_watcher.Observer")
def test_file_change_monitoring(mock_observer, mock_transformer, mock_qdrant, sample_project_dir):
    """Test file change monitoring"""
    # Setup mocks
    mock_model = MagicMock()
    mock_model.encode.return_value = [0.1, 0.2, 0.3, 0.4, 0.5]
    mock_model.get_sentence_embedding_dimension.return_value = 5
    mock_transformer.return_value = mock_model

    mock_client = MagicMock()
    mock_qdrant.return_value = mock_client

    # Create vector search engine
    vector_search = VectorSearch(
        host="localhost", port=6333, embedding_model="test-model", collection_name="test-collection"
    )

    # Create file processor with spy on handle_file_change
    file_processor = FileProcessor(
        vector_search=vector_search,
        project_path=str(sample_project_dir),
        ignore_patterns=[".git", "*.pyc"],
        data_dir=str(sample_project_dir / "data"),
    )
    file_processor.handle_file_change = MagicMock(wraps=file_processor.handle_file_change)

    # Create file watcher
    file_watcher = FileWatcher(
        project_path=str(sample_project_dir),
        ignore_patterns=[".git", "*.pyc"],
        on_file_change=file_processor.handle_file_change,
    )

    # Start file watcher
    file_watcher.start()

    # Simulate file change event
    event_handler = mock_observer.return_value.schedule.call_args[0][0]

    # Create a fake event with src_path
    class FakeEvent:
        is_directory = False
        src_path = str(sample_project_dir / "src" / "new_file.py")

    # Trigger created event
    event_handler.on_created(FakeEvent())

    # Verify handle_file_change was called
    file_processor.handle_file_change.assert_called_with("created", FakeEvent.src_path)

    # Cleanup
    file_watcher.stop()
