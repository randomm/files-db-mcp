#!/bin/bash
# Startup script for Files-DB-MCP

# Stop on error
set -e

# Detect project directory
PROJECT_DIR=$(pwd)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Print banner
echo "=================================================="
echo "  Files-DB-MCP - Vector Search for Code Projects  "
echo "=================================================="
echo
echo "Starting Files-DB-MCP for project: $PROJECT_DIR"
echo

# Check if Docker and Docker Compose are installed
if ! command -v docker >/dev/null 2>&1; then
    echo "Error: Docker is not installed or not in PATH"
    echo "Please install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! docker compose version >/dev/null 2>&1; then
    echo "Error: Docker Compose is not installed or not in PATH"
    echo "Please install Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

# Set environment variables
export PROJECT_DIR=$PROJECT_DIR

# Stop and remove any existing containers from previous runs
echo "Cleaning up any existing containers..."
if [ "$SCRIPT_DIR" != "$PROJECT_DIR" ]; then
    # Using absolute path to docker-compose.yml
    docker compose -f "$SCRIPT_DIR/docker-compose.yml" down
else
    # Running from project directory
    docker compose down
fi

# Run Docker Compose with proper timeout for startup
echo "Starting Docker Compose services..."
if [ "$SCRIPT_DIR" != "$PROJECT_DIR" ]; then
    # Running from different directory, use absolute path to docker-compose.yml
    COMPOSE_HTTP_TIMEOUT=300 docker compose -f "$SCRIPT_DIR/docker-compose.yml" up --build -d
else
    # Running from project directory
    COMPOSE_HTTP_TIMEOUT=300 docker compose up --build -d
fi

# Wait for services to be healthy
echo 
echo "Files-DB-MCP is starting up..."
echo "Waiting for services to become healthy..."

# Wait up to 2 minutes for services to be healthy
timeout=120
interval=5
elapsed=0

while [ $elapsed -lt $timeout ]; do
    # Check if vector-db is healthy
    VECTOR_DB_STATUS=$(docker inspect --format='{{.State.Health.Status}}' files-db-mcp-vector-db-1 2>/dev/null || echo "container not found")
    
    # Check if files-db-mcp is healthy
    MCP_STATUS=$(docker inspect --format='{{.State.Health.Status}}' files-db-mcp-files-db-mcp-1 2>/dev/null || echo "container not found")
    
    echo -n "Vector DB: $VECTOR_DB_STATUS, MCP: $MCP_STATUS"
    echo
    
    if [ "$VECTOR_DB_STATUS" = "healthy" ] && [ "$MCP_STATUS" = "healthy" ]; then
        echo "All services are healthy!"
        break
    fi
    
    sleep $interval
    elapsed=$((elapsed + interval))
    echo -n "."
done

if [ $elapsed -ge $timeout ]; then
    echo "Timeout waiting for services to become healthy."
    echo "Check container logs with: docker logs files-db-mcp-vector-db-1"
    echo "Check container logs with: docker logs files-db-mcp-files-db-mcp-1"
    exit 1
fi

echo
echo "Files-DB-MCP is ready!"
echo "Indexing is running in the background."
echo "You can now connect to the MCP interface at http://localhost:3000"
echo
echo "To check indexing status: curl http://localhost:3000/health"
echo "To stop the service: docker compose down"
echo
echo "Services are running in the background. Happy coding!"