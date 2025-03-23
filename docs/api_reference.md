# Files-DB-MCP API Reference

This document provides a comprehensive reference for all APIs exposed by Files-DB-MCP.

## API Endpoints Overview

Files-DB-MCP exposes the following types of APIs:

1. **MCP Interface** - For integration with Claude Code and other LLM tools
2. **HTTP REST API** - For direct programmatic access
3. **SSE API** - For real-time updates and streaming results

## 1. MCP Interface API

The Message Control Protocol (MCP) interface allows AI tools like Claude Code to interact with the vector database.

### MCP Functions

#### `search_files`

Search for files by content similarity with advanced filtering.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| query | string | Yes | The search query text |
| limit | integer | No | Maximum results to return (default: 10) |
| file_type | string | No | Filter by file type |
| path_prefix | string | No | Filter by path prefix |
| file_extensions | array of string | No | Filter by file extensions (e.g., ["py", "js"]) |
| modified_after | number | No | Filter by modification time (timestamp) |
| modified_before | number | No | Filter by modification time (timestamp) |
| exclude_paths | array of string | No | Exclude paths containing these strings |
| custom_metadata | object | No | Custom metadata filters |
| threshold | number | No | Minimum similarity score (default: 0.6) |

**Example:**

```json
{
  "function": "search_files",
  "parameters": {
    "query": "database connection",
    "limit": 5,
    "file_extensions": ["py", "js"],
    "path_prefix": "src/"
  },
  "request_id": "search-request-1"
}
```

**Response:**

```json
{
  "success": true,
  "results": [
    {
      "file_path": "src/database.py",
      "score": 0.85,
      "snippet": "def connect_to_database():\n    # Establish connection to the database\n    ...",
      "metadata": {
        "file_type": "python",
        "file_size": 1024,
        "last_modified": 1616161616
      }
    },
    // Additional results...
  ],
  "count": 1,
  "filters": {
    "file_extensions": ["py", "js"],
    "path_prefix": "src/",
    "threshold": 0.6
  },
  "request_id": "search-request-1"
}
```

#### `get_file_content`

Retrieve the content of a specific file.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| file_path | string | Yes | Path to the file |

**Example:**

```json
{
  "function": "get_file_content",
  "parameters": {
    "file_path": "src/database.py"
  },
  "request_id": "content-request-1"
}
```

**Response:**

```json
{
  "success": true,
  "file_path": "src/database.py",
  "content": "def connect_to_database():\n    # Establish connection to the database\n    ...",
  "request_id": "content-request-1"
}
```

#### `get_model_info`

Get information about the current embedding model.

**Parameters:** None

**Example:**

```json
{
  "function": "get_model_info",
  "parameters": {},
  "request_id": "model-info-request-1"
}
```

**Response:**

```json
{
  "success": true,
  "model_info": {
    "model_name": "sentence-transformers/all-MiniLM-L6-v2",
    "dimension": 384,
    "quantization": true,
    "binary_embeddings": false
  },
  "request_id": "model-info-request-1"
}
```

#### `trigger_reindex`

Trigger a reindexing of files.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| incremental | boolean | No | Whether to use incremental indexing (default: true) |

**Example:**

```json
{
  "function": "trigger_reindex",
  "parameters": {
    "incremental": false
  },
  "request_id": "reindex-request-1"
}
```

**Response:**

```json
{
  "success": true,
  "message": "Started full reindexing",
  "request_id": "reindex-request-1"
}
```

#### `get_indexing_status`

Get current indexing status.

**Parameters:** None

**Example:**

```json
{
  "function": "get_indexing_status",
  "parameters": {},
  "request_id": "status-request-1"
}
```

**Response:**

```json
{
  "success": true,
  "is_complete": true,
  "progress": 100.0,
  "files_indexed": 1250,
  "total_files": 1250,
  "request_id": "status-request-1"
}
```

### MCP Resources

MCP resources provide access to additional information about the vector search system.

#### `vector-search://stats`

Get statistics about the vector search engine.

**Response:**

```json
{
  "total_files_indexed": 1250,
  "collection_name": "files",
  "model_name": "sentence-transformers/all-MiniLM-L6-v2",
  "dimension": 384,
  "server_address": "localhost:6333"
}
```

### MCP Prompts

MCP prompts provide pre-defined content for specific use cases.

#### `vector_search_help`

Get help on using the vector search functionality.

**Response:** Markdown-formatted help text for vector search usage.

## 2. HTTP REST API

Files-DB-MCP also exposes a RESTful HTTP API for direct programmatic access.

### Endpoints

#### `GET /health`

Check the health status of the service.

**Response:**

```json
{
  "status": "healthy",
  "vector_db": "connected",
  "indexed_files": 1250,
  "total_files": 1250,
  "indexing_progress": 100.0
}
```

#### `POST /mcp`

Send an MCP command to the service.

**Request Body:**

```json
{
  "function": "search_files",
  "parameters": {
    "query": "database connection",
    "limit": 5
  },
  "request_id": "search-request-1"
}
```

**Response:** Same as the corresponding MCP function response.

## 3. SSE API

The Server-Sent Events (SSE) API allows clients to receive real-time updates.

### Endpoints

#### `GET /sse/indexing-progress`

Stream indexing progress updates.

**Events:**

- `progress`: Indexing progress update
  ```json
  {
    "indexed_files": 750,
    "total_files": 1000,
    "progress": 75.0
  }
  ```

- `complete`: Indexing completed notification
  ```json
  {
    "indexed_files": 1000,
    "total_files": 1000,
    "progress": 100.0,
    "time_taken_seconds": 45
  }
  ```

#### `GET /sse/search?query={query}`

Stream search results as they become available.

**Events:**

- `result`: Individual search result
  ```json
  {
    "file_path": "src/database.py",
    "score": 0.85,
    "rank": 1
  }
  ```

- `complete`: Search completed notification
  ```json
  {
    "total_results": 5,
    "time_taken_ms": 250
  }
  ```

## API Versioning

Files-DB-MCP follows semantic versioning for its APIs. Breaking changes will be introduced only in major version updates.

## Authentication

Currently, the API does not require authentication. For production use, it's recommended to secure the API behind an authentication proxy.

## Error Handling

All APIs follow a consistent error format:

```json
{
  "success": false,
  "error": "Error message description",
  "error_code": "ERROR_CODE",
  "request_id": "original-request-id"
}
```

Common error codes:

- `INVALID_REQUEST`: Malformed request
- `NOT_FOUND`: Requested resource not found
- `INTERNAL_ERROR`: Server-side error
- `UNAUTHORIZED`: Authentication required or failed