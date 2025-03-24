"""
Server-Sent Events (SSE) implementation for the MCP interface
"""

import asyncio
import json
import logging
import time
from enum import Enum
from typing import Any, AsyncGenerator, Dict, List, Optional

from fastapi import APIRouter, FastAPI, Request
from pydantic import BaseModel, Field
from sse_starlette.sse import EventSourceResponse

logger = logging.getLogger("files-db-mcp.sse_interface")


# Event types
class EventType(str, Enum):
    INDEXING_PROGRESS = "indexing_progress"
    SEARCH_RESULTS = "search_results"
    ERROR = "error"
    NOTIFICATION = "notification"


# Models for SSE endpoints
class SearchQuery(BaseModel):
    query: str
    limit: int = 10
    file_type: Optional[str] = None
    path_prefix: Optional[str] = None
    file_extensions: Optional[List[str]] = None
    modified_after: Optional[float] = None
    modified_before: Optional[float] = None
    exclude_paths: Optional[List[str]] = None
    custom_metadata: Optional[Dict[str, Any]] = None
    threshold: float = 0.6


class ProgressUpdate(BaseModel):
    total_files: int
    files_indexed: int
    percentage: float
    status: str
    message: Optional[str] = None
    timestamp: float = Field(default_factory=time.time)


class SSEInterface:
    """
    Server-Sent Events (SSE) interface for the MCP service
    """

    def __init__(self, app: FastAPI, vector_search, file_processor):
        """
        Initialize the SSE interface

        Args:
            app: FastAPI application
            vector_search: Vector search engine
            file_processor: File processor
        """
        self.app = app
        self.vector_search = vector_search
        self.file_processor = file_processor
        self.router = APIRouter()

        # Keep track of active SSE connections
        self.active_connections: Dict[str, asyncio.Queue] = {}

        # Set up routes
        self.setup_routes()

        # Register router with app
        self.app.include_router(self.router, prefix="/sse", tags=["sse"])

        # Store coroutine for later execution when asyncio loop is running
        self._progress_task = None
        
        # Start background task on startup
        @app.on_event("startup")
        async def start_background_tasks():
            self._progress_task = asyncio.create_task(self._indexing_progress_task())

    def setup_routes(self):
        """Set up SSE routes"""

        @self.router.get("/events")
        async def sse_events(request: Request, client_id: Optional[str] = None):
            """
            SSE endpoint for events

            Args:
                request: FastAPI request
                client_id: Optional client ID for reconnection
            """
            if client_id is None:
                client_id = f"client_{time.time()}_{id(request)}"

            # Create queue for this client
            queue = asyncio.Queue()
            self.active_connections[client_id] = queue

            # Remove connection when client disconnects
            try:
                return EventSourceResponse(self._event_generator(client_id, queue))
            finally:
                await self._cleanup_connection(client_id)

        @self.router.get("/indexing-progress")
        async def indexing_progress(request: Request):
            """
            SSE endpoint for indexing progress updates
            """
            client_id = f"progress_{time.time()}_{id(request)}"
            queue = asyncio.Queue()
            self.active_connections[client_id] = queue

            # Send initial progress
            await self._send_indexing_progress(client_id)

            try:
                return EventSourceResponse(self._event_generator(client_id, queue))
            finally:
                await self._cleanup_connection(client_id)

        @self.router.post("/search")
        async def search(request: Request, query: SearchQuery):
            """
            SSE endpoint for search results
            """
            client_id = f"search_{time.time()}_{id(request)}"
            queue = asyncio.Queue()
            self.active_connections[client_id] = queue

            # Start search in background
            search_task = asyncio.create_task(
                self._perform_search(
                    client_id=client_id,
                    query=query.query,
                    limit=query.limit,
                    file_type=query.file_type,
                    threshold=query.threshold,
                )
            )
            # Store task reference to prevent it from being garbage collected
            client_id_key = f"search_task_{client_id}"
            setattr(self, client_id_key, search_task)

            try:
                return EventSourceResponse(self._event_generator(client_id, queue))
            finally:
                await self._cleanup_connection(client_id)

    async def _event_generator(
        self, client_id: str, queue: asyncio.Queue
    ) -> AsyncGenerator[Dict[str, str], None]:
        """
        Generate SSE events from queue

        Args:
            client_id: Client ID
            queue: Event queue

        Yields:
            SSE events
        """
        try:
            while True:
                # Wait for event
                event = await queue.get()

                # Check for stop signal
                if event.get("type") == "close":
                    break

                yield event

                # Mark as done
                queue.task_done()
        except asyncio.CancelledError:
            logger.info(f"Connection closed for client {client_id}")
            raise
        except Exception as e:
            logger.error(f"Error in event generator for client {client_id}: {e!s}")
            # Send error event
            yield {"event": EventType.ERROR, "data": json.dumps({"error": f"{e}"})}
            raise

    async def _cleanup_connection(self, client_id: str):
        """
        Clean up connection for client

        Args:
            client_id: Client ID
        """
        if client_id in self.active_connections:
            # Try to add close event to queue
            import contextlib
            with contextlib.suppress(Exception):
                await self.active_connections[client_id].put({"type": "close"})

            # Remove client
            del self.active_connections[client_id]
            logger.info(f"Removed client {client_id}")

    async def _indexing_progress_task(self):
        """Background task for sending indexing progress updates"""
        try:
            last_progress = -1
            while True:
                # Only send updates if there are active connections interested in progress
                active_progress_clients = [
                    client_id
                    for client_id in self.active_connections
                    if client_id.startswith("progress_")
                ]

                if active_progress_clients and self.file_processor:
                    # Get current progress
                    current_progress = int(self.file_processor.get_indexing_progress())

                    # Only send if progress has changed significantly
                    if current_progress != last_progress:
                        last_progress = current_progress

                        # Send progress update to all interested clients
                        for client_id in active_progress_clients:
                            await self._send_indexing_progress(client_id)

                # Wait before checking again
                await asyncio.sleep(1)
        except Exception as e:
            logger.error(f"Error in indexing progress task: {e!s}")

    async def _send_indexing_progress(self, client_id: str):
        """
        Send indexing progress update to client

        Args:
            client_id: Client ID
        """
        if self.file_processor and client_id in self.active_connections:
            # Create progress update
            progress = ProgressUpdate(
                total_files=self.file_processor.get_total_files(),
                files_indexed=self.file_processor.get_files_indexed(),
                percentage=self.file_processor.get_indexing_progress(),
                status="indexing" if not self.file_processor.is_indexing_complete() else "complete",
                message=f"Indexed {self.file_processor.get_files_indexed()} of {self.file_processor.get_total_files()} files",
            )

            # Send event
            await self.active_connections[client_id].put(
                {"event": EventType.INDEXING_PROGRESS, "data": progress.model_dump_json()}
            )

    async def _perform_search(
        self, client_id: str, query: str, limit: int, file_type: Optional[str], threshold: float
    ):
        """
        Perform search and send results to client

        Args:
            client_id: Client ID
            query: Search query
            limit: Maximum number of results
            file_type: Optional file type filter
            threshold: Similarity threshold
        """
        try:
            # Check if client is still connected
            if client_id not in self.active_connections:
                return

            # Send notification that search is starting
            await self.active_connections[client_id].put(
                {
                    "event": EventType.NOTIFICATION,
                    "data": json.dumps({"message": "Search started", "query": query}),
                }
            )

            # Perform search
            results = self.vector_search.search(
                query=query, limit=limit, file_type=file_type, threshold=threshold
            )

            # Check if client is still connected
            if client_id not in self.active_connections:
                return

            # Send results
            await self.active_connections[client_id].put(
                {
                    "event": EventType.SEARCH_RESULTS,
                    "data": json.dumps({"query": query, "count": len(results), "results": results}),
                }
            )

            # Send close event
            await self.active_connections[client_id].put({"type": "close"})
        except Exception as e:
            logger.error(f"Error in search for client {client_id}: {e!s}")

            # Send error if client is still connected
            if client_id in self.active_connections:
                await self.active_connections[client_id].put(
                    {"event": EventType.ERROR, "data": json.dumps({"error": f"{e}"})}
                )

                # Send close event
                await self.active_connections[client_id].put({"type": "close"})

    async def broadcast(self, event_type: EventType, data: Any):
        """
        Broadcast event to all connected clients

        Args:
            event_type: Event type
            data: Event data
        """
        for client_id, queue in self.active_connections.items():
            try:
                await queue.put(
                    {
                        "event": event_type,
                        "data": json.dumps(data) if not isinstance(data, str) else data,
                    }
                )
            except Exception as e:
                logger.error(f"Error broadcasting to client {client_id}: {e!s}")

    async def send_notification(self, client_id: str, message: str):
        """
        Send notification to specific client

        Args:
            client_id: Client ID
            message: Notification message
        """
        if client_id in self.active_connections:
            await self.active_connections[client_id].put(
                {"event": EventType.NOTIFICATION, "data": json.dumps({"message": message})}
            )

    async def close_all_connections(self):
        """Close all SSE connections"""
        for client_id in list(self.active_connections.keys()):
            await self._cleanup_connection(client_id)
