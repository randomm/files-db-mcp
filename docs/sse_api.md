# Server-Sent Events (SSE) API

Files-DB-MCP provides Server-Sent Events (SSE) endpoints for real-time updates and streaming search results. This document describes how to use the SSE API.

## Overview

Server-Sent Events (SSE) is a standard that enables servers to push real-time updates to clients over HTTP connections. Files-DB-MCP uses SSE to provide:

1. Real-time indexing progress updates
2. Streaming search results
3. Notifications for system events

## Endpoints

The SSE API is available at the following endpoints:

### `GET /sse/events`

General-purpose event stream for all events. Use this endpoint to receive all events from the system.

**Parameters:**
- `client_id` (optional): Client identifier for reconnection

**Example:**
```javascript
const eventsource = new EventSource('http://localhost:3000/sse/events');
eventsource.addEventListener('indexing_progress', (event) => {
  const data = JSON.parse(event.data);
  console.log(`Indexing progress: ${data.percentage}%`);
});
eventsource.addEventListener('search_results', (event) => {
  const data = JSON.parse(event.data);
  console.log(`Search results: ${data.count} matches`);
});
```

### `GET /sse/indexing-progress`

Event stream specifically for indexing progress updates. Use this endpoint to track the progress of file indexing.

**Example:**
```javascript
const progressSource = new EventSource('http://localhost:3000/sse/indexing-progress');
progressSource.addEventListener('indexing_progress', (event) => {
  const data = JSON.parse(event.data);
  console.log(`Indexed ${data.files_indexed} of ${data.total_files} files (${data.percentage}%)`);
  console.log(`Status: ${data.status}`);
  console.log(`Message: ${data.message}`);
});
```

### `POST /sse/search`

Perform a search and receive results via SSE stream.

**Request Body:**
```json
{
  "query": "function definition",
  "limit": 10,
  "file_type": "py",
  "threshold": 0.6
}
```

**Parameters:**
- `query` (required): The search query
- `limit` (optional): Maximum number of results (default: 10)
- `file_type` (optional): Filter by file type (e.g., "py", "js")
- `threshold` (optional): Similarity threshold (default: 0.6)

**Example:**
```javascript
// Set up EventSource for the search results
const searchEventSource = new EventSource('http://localhost:3000/sse/search');

// Listen for search results
searchEventSource.addEventListener('search_results', (event) => {
  const data = JSON.parse(event.data);
  console.log(`Search results for "${data.query}":`);
  console.log(`Found ${data.count} results`);
  
  // Process each result
  data.results.forEach((result, index) => {
    console.log(`Result ${index + 1}: ${result.file_path} (score: ${result.score})`);
  });
});

// Listen for notifications
searchEventSource.addEventListener('notification', (event) => {
  const data = JSON.parse(event.data);
  console.log(`Notification: ${data.message}`);
});

// Listen for errors
searchEventSource.addEventListener('error', (event) => {
  const data = JSON.parse(event.data);
  console.error(`Error: ${data.error}`);
});

// Perform search
fetch('http://localhost:3000/sse/search', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    query: "function definition",
    limit: 10,
    file_type: "py"
  })
});
```

## Event Types

The SSE API uses the following event types:

### `indexing_progress`

Provides updates on the file indexing process.

**Data format:**
```json
{
  "total_files": 100,
  "files_indexed": 50,
  "percentage": 50.0,
  "status": "indexing",
  "message": "Indexed 50 of 100 files",
  "timestamp": 1616493715.654321
}
```

### `search_results`

Provides search results for a query.

**Data format:**
```json
{
  "query": "function definition",
  "count": 2,
  "results": [
    {
      "file_path": "src/main.py",
      "file_type": "py",
      "content": "def main():\n    print('Hello, world!')",
      "score": 0.95
    },
    {
      "file_path": "src/utils.py",
      "file_type": "py",
      "content": "def helper():\n    return 'Helper function'",
      "score": 0.85
    }
  ]
}
```

### `notification`

Provides general notifications.

**Data format:**
```json
{
  "message": "Search started",
  "query": "function definition"
}
```

### `error`

Provides error messages.

**Data format:**
```json
{
  "error": "Invalid search parameters"
}
```

## Connection Management

- Connections are automatically closed after sending search results
- Long-polling is used for indexing progress updates
- The server may close connections after a period of inactivity
- Clients should implement reconnection logic for robustness

## Cross-Origin Resource Sharing (CORS)

The SSE API supports Cross-Origin Resource Sharing (CORS), allowing it to be accessed from web applications hosted on different domains. All origins are allowed by default.