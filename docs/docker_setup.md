# Docker Setup Guide for Files-DB-MCP

This document provides instructions for setting up and using Files-DB-MCP with Docker Compose.

## Prerequisites

- Docker and Docker Compose installed on your system
- Basic familiarity with command-line operations

## Quick Start

1. Start the Files-DB-MCP services with a single command:

```bash
# From any project directory
PROJECT_DIR=$(pwd) docker-compose -f /path/to/files-db-mcp/docker-compose.yml up -d
```

2. Once started, the services will be available at:
   - MCP Interface: `http://localhost:3000/mcp`
   - Health Check: `http://localhost:3000/health`

3. To stop the services:

```bash
docker-compose -f /path/to/files-db-mcp/docker-compose.yml down
```

## Important Notes

- **First-time startup**: The first time you start the container, it may take 3-5 minutes to fully initialize as it downloads the embedding model. Subsequent startups will be much faster.
- **Health check status**: You can monitor the health status of the containers with `docker-compose ps` - wait for the status to change from "starting" to running (no status label).
- **Project directory**: The `PROJECT_DIR` environment variable should point to the directory containing the code you want to index and search.

## Docker Compose Configuration

The Docker Compose setup consists of two main services:

1. **vector-db**: A Qdrant vector database for storing and searching file embeddings
   - Exposed on port 6333
   - Uses a persistent volume for data storage

2. **files-db-mcp**: The main service that handles file indexing and MCP interface
   - Exposed on port 3000 (maps to internal port 8000)
   - Mounts the project directory as read-only
   - Uses a persistent volume for internal data

## Common Issues and Solutions

### Long Startup Time
- The initial startup takes longer due to embedding model downloads
- Subsequent startups should be faster as models are cached

### Health Check Failures
- If health checks fail consistently, check the logs with `docker-compose logs files-db-mcp`
- Most common cause is the model download taking longer than expected

### Testing the Setup

You can test if the system is working correctly with this simple Python script:

```python
import requests
import json

# Test health endpoint
health_response = requests.get("http://localhost:3000/health")
print(f"Health check status: {health_response.status_code}")
print(f"Health check response: {health_response.json()}\n")

# Test MCP endpoint with a simple search query
mcp_request = {
    "function": "search_files",
    "parameters": {
        "query": "your search term",
        "limit": 5
    },
    "request_id": "test_request_123"
}

mcp_response = requests.post(
    "http://localhost:3000/mcp", 
    json=mcp_request
)

print(f"MCP endpoint status: {mcp_response.status_code}")
print(f"MCP response: {json.dumps(mcp_response.json(), indent=2)}")
```

## Environment Variables

The following environment variables can be set to customize the Docker setup:

| Variable | Description | Default |
|----------|-------------|---------|
| PROJECT_DIR | Path to the project directory to be indexed | Current directory (./)|
| VECTOR_DB_HOST | Hostname for the vector database | vector-db |
| VECTOR_DB_PORT | Port for the vector database | 6333 |
| EMBEDDING_MODEL | Model to use for embeddings | sentence-transformers/all-MiniLM-L6-v2 |
| QUANTIZATION | Enable model quantization | true |
| BINARY_EMBEDDINGS | Use binary embeddings | false |
| DEBUG | Enable debug mode | true |
| IGNORE_PATTERNS | Patterns to ignore during indexing | .git,node_modules,__pycache__,venv,dist,build,*.pyc,.files-db-mcp |
| PORT | Port for the MCP interface | 8000 |