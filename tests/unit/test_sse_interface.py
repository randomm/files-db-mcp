"""
Unit tests for the SSE interface module
"""

import asyncio
import json
from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI

from src.sse_interface import EventType, SSEInterface


@pytest.fixture
def app():
    """Create FastAPI app for testing"""
    return FastAPI()


@pytest.fixture
def mock_vector_search():
    """Mock vector search for testing"""
    mock = MagicMock()
    mock.search.return_value = [
        {
            "file_path": "src/main.py",
            "file_type": "py",
            "content": "# Main file content",
            "score": 0.95,
        }
    ]
    return mock


@pytest.fixture
def mock_file_processor():
    """Mock file processor for testing"""
    mock = MagicMock()
    mock.get_total_files.return_value = 100
    mock.get_files_indexed.return_value = 50
    mock.get_indexing_progress.return_value = 50.0
    mock.is_indexing_complete.return_value = False
    return mock


def test_sse_interface_init(app, mock_vector_search, mock_file_processor):
    """Test SSE interface initialization"""
    # Patch asyncio.create_task to prevent actual task creation
    with patch('asyncio.create_task') as mock_create_task:
        # Create SSE interface
        sse = SSEInterface(
            app=app,
            vector_search=mock_vector_search,
            file_processor=mock_file_processor,
        )

    # Verify routes were set up
    assert any(route.path == "/sse/events" for route in app.routes)
    assert any(route.path == "/sse/indexing-progress" for route in app.routes)
    assert any(route.path == "/sse/search" for route in app.routes)


@pytest.mark.asyncio
async def test_send_indexing_progress(app, mock_vector_search, mock_file_processor):
    """Test sending indexing progress"""
    # Patch asyncio.create_task to prevent actual task creation
    with patch('asyncio.create_task') as mock_create_task:
        # Create SSE interface
        sse = SSEInterface(
            app=app,
            vector_search=mock_vector_search,
            file_processor=mock_file_processor,
        )

    # Create client ID and queue
    client_id = "test_client"
    queue = asyncio.Queue()
    sse.active_connections[client_id] = queue

    # Send indexing progress
    await sse._send_indexing_progress(client_id)

    # Get event from queue
    event = await queue.get()

    # Verify event
    assert event["event"] == EventType.INDEXING_PROGRESS

    # Parse data
    data = json.loads(event["data"])
    assert data["total_files"] == 100
    assert data["files_indexed"] == 50
    assert data["percentage"] == 50.0
    assert data["status"] == "indexing"
    assert "message" in data
    assert "timestamp" in data


@pytest.mark.asyncio
async def test_perform_search(app, mock_vector_search, mock_file_processor):
    """Test performing search"""
    # Patch asyncio.create_task to prevent actual task creation
    with patch('asyncio.create_task') as mock_create_task:
        # Create SSE interface
        sse = SSEInterface(
            app=app,
            vector_search=mock_vector_search,
            file_processor=mock_file_processor,
        )

    # Create client ID and queue
    client_id = "test_search"
    queue = asyncio.Queue()
    sse.active_connections[client_id] = queue

    # Perform search
    await sse._perform_search(
        client_id=client_id,
        query="test query",
        limit=10,
        file_type="py",
        threshold=0.5,
    )

    # Get notification event
    notification = await queue.get()
    assert notification["event"] == EventType.NOTIFICATION

    # Get search results event
    results = await queue.get()
    assert results["event"] == EventType.SEARCH_RESULTS

    # Parse data
    data = json.loads(results["data"])
    assert data["query"] == "test query"
    assert data["count"] == 1
    assert len(data["results"]) == 1
    assert data["results"][0]["file_path"] == "src/main.py"

    # Verify search was called with correct parameters
    mock_vector_search.search.assert_called_once_with(
        query="test query",
        limit=10,
        file_type="py",
        threshold=0.5,
    )

    # Get close event
    close = await queue.get()
    assert close["type"] == "close"


@pytest.mark.asyncio
async def test_broadcast(app, mock_vector_search, mock_file_processor):
    """Test broadcasting events to all clients"""
    # Patch asyncio.create_task to prevent actual task creation
    with patch('asyncio.create_task') as mock_create_task:
        # Create SSE interface
        sse = SSEInterface(
            app=app,
            vector_search=mock_vector_search,
            file_processor=mock_file_processor,
        )

    # Create multiple client queues
    client1_queue = asyncio.Queue()
    client2_queue = asyncio.Queue()
    client3_queue = asyncio.Queue()
    
    sse.active_connections = {
        "client1": client1_queue,
        "client2": client2_queue,
        "client3": client3_queue,
    }

    # Broadcast a notification to all clients
    test_data = {"message": "Test broadcast", "status": "ok"}
    await sse.broadcast(EventType.NOTIFICATION, test_data)

    # Check that all clients received the message
    for queue in [client1_queue, client2_queue, client3_queue]:
        event = await queue.get()
        assert event["event"] == EventType.NOTIFICATION
        data = json.loads(event["data"])
        assert data["message"] == "Test broadcast"
        assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_send_notification(app, mock_vector_search, mock_file_processor):
    """Test sending notification to a specific client"""
    # Patch asyncio.create_task to prevent actual task creation
    with patch('asyncio.create_task') as mock_create_task:
        # Create SSE interface
        sse = SSEInterface(
            app=app,
            vector_search=mock_vector_search,
            file_processor=mock_file_processor,
        )

    # Create client ID and queue
    client_id = "test_notification"
    queue = asyncio.Queue()
    sse.active_connections[client_id] = queue

    # Send notification
    await sse.send_notification(client_id, "Test notification message")

    # Get notification event
    notification = await queue.get()
    
    # Verify event
    assert notification["event"] == EventType.NOTIFICATION
    data = json.loads(notification["data"])
    assert data["message"] == "Test notification message"

    # Test with non-existent client
    # This should not raise an exception
    await sse.send_notification("non_existent_client", "This should not cause an error")


@pytest.mark.asyncio
async def test_cleanup_connection(app, mock_vector_search, mock_file_processor):
    """Test cleaning up a connection"""
    # Patch asyncio.create_task to prevent actual task creation
    with patch('asyncio.create_task') as mock_create_task:
        # Create SSE interface
        sse = SSEInterface(
            app=app,
            vector_search=mock_vector_search,
            file_processor=mock_file_processor,
        )

    # Create client ID and queue
    client_id = "test_cleanup"
    queue = asyncio.Queue()
    sse.active_connections[client_id] = queue

    # Cleanup connection
    await sse._cleanup_connection(client_id)

    # Verify client was removed
    assert client_id not in sse.active_connections

    # Test with non-existent client (should not raise exception)
    await sse._cleanup_connection("non_existent_client")


@pytest.mark.asyncio
async def test_close_all_connections(app, mock_vector_search, mock_file_processor):
    """Test closing all connections"""
    # Patch asyncio.create_task to prevent actual task creation
    with patch('asyncio.create_task') as mock_create_task:
        # Create SSE interface
        sse = SSEInterface(
            app=app,
            vector_search=mock_vector_search,
            file_processor=mock_file_processor,
        )

    # Create multiple client connections
    sse.active_connections = {
        "client1": asyncio.Queue(),
        "client2": asyncio.Queue(),
        "client3": asyncio.Queue(),
    }

    # Close all connections
    await sse.close_all_connections()

    # Verify all clients were removed
    assert len(sse.active_connections) == 0


@pytest.mark.asyncio
async def test_perform_search_with_exception(app, mock_vector_search, mock_file_processor):
    """Test performing search with exception"""
    # Patch asyncio.create_task to prevent actual task creation
    with patch('asyncio.create_task') as mock_create_task:
        # Create SSE interface
        sse = SSEInterface(
            app=app,
            vector_search=mock_vector_search,
            file_processor=mock_file_processor,
        )

    # Create client ID and queue
    client_id = "test_search_error"
    queue = asyncio.Queue()
    sse.active_connections[client_id] = queue

    # Modify mock to raise an exception
    mock_vector_search.search.side_effect = ValueError("Test search error")

    # Perform search
    await sse._perform_search(
        client_id=client_id,
        query="test query",
        limit=10,
        file_type="py",
        threshold=0.5,
    )

    # Get notification event
    notification = await queue.get()
    assert notification["event"] == EventType.NOTIFICATION

    # Get error event
    error = await queue.get()
    assert error["event"] == EventType.ERROR
    data = json.loads(error["data"])
    assert "error" in data
    assert "Test search error" in data["error"]

    # Get close event
    close = await queue.get()
    assert close["type"] == "close"
