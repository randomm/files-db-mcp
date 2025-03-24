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

# Get the repository base directory
BASE_DIR="$(dirname "$SCRIPT_DIR")"

# Stop and remove any existing containers from previous runs
echo "Cleaning up any existing containers..."
if [ "$PROJECT_DIR" != "$BASE_DIR" ]; then
    # Using absolute path to docker-compose.yml
    docker compose -f "$BASE_DIR/docker-compose.yml" down
else
    # Running from project directory
    docker compose down
fi

# Check if docker-compose.yml exists in the base directory
if [ ! -f "$BASE_DIR/docker-compose.yml" ]; then
    echo "Error: docker-compose.yml not found at $BASE_DIR/docker-compose.yml"
    echo "This usually happens when the installation paths are incorrect."
    
    # Check the common installation directory
    if [ -f "$HOME/.files-db-mcp/docker-compose.yml" ]; then
        echo "Found docker-compose.yml in the default installation directory."
        BASE_DIR="$HOME/.files-db-mcp"
        echo "Using $BASE_DIR as the base directory."
    else
        echo "Could not find docker-compose.yml in the expected locations."
        echo "Please make sure files-db-mcp is properly installed."
        exit 1
    fi
fi

# Run Docker Compose with proper timeout for startup
echo "Starting Docker Compose services..."
# Use the docker-compose.yml from the base directory
COMPOSE_HTTP_TIMEOUT=300 docker compose -f "$BASE_DIR/docker-compose.yml" up --build -d

# Wait for services to start
echo 
echo "Files-DB-MCP is starting up..."
echo "Waiting for services to initialize..."

# Get the actual container names as they might be different
MCP_CONTAINER=$(docker compose -f "$BASE_DIR/docker-compose.yml" ps -q files-db-mcp)
VECTOR_DB_CONTAINER=$(docker compose -f "$BASE_DIR/docker-compose.yml" ps -q vector-db)

echo "Container IDs: MCP=$MCP_CONTAINER, Vector DB=$VECTOR_DB_CONTAINER"

# Wait up to 2 minutes for MCP to become healthy
timeout=120
interval=5
elapsed=0

echo "Waiting for MCP service to become healthy..."
while [ $elapsed -lt $timeout ]; do
    # Check if files-db-mcp is healthy
    if [ ! -z "$MCP_CONTAINER" ]; then
        MCP_STATUS=$(docker inspect --format='{{if .State.Health}}{{.State.Health.Status}}{{else}}no health check{{end}}' "$MCP_CONTAINER" 2>/dev/null || echo "error")
        echo -n "MCP Status: $MCP_STATUS"
        echo
        
        if [ "$MCP_STATUS" = "healthy" ]; then
            echo "MCP service is healthy!"
            break
        fi
    else
        echo "MCP container not found"
    fi
    
    sleep $interval
    elapsed=$((elapsed + interval))
    echo -n "."
done

if [ $elapsed -ge $timeout ]; then
    echo "Timeout waiting for MCP service to become healthy."
    echo "Check MCP container logs with: docker logs $MCP_CONTAINER"
    echo "Check Vector DB container logs with: docker logs $VECTOR_DB_CONTAINER"
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