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

# Run Docker Compose
echo "Starting Docker Compose services..."
if [ "$SCRIPT_DIR" != "$PROJECT_DIR" ]; then
    # Running from different directory, use absolute path to docker-compose.yml
    docker compose -f "$SCRIPT_DIR/docker-compose.yml" up --build -d
else
    # Running from project directory
    docker compose up --build -d
fi

# Show status
echo
echo "Files-DB-MCP is starting up..."
echo "Indexing will begin automatically in the background."
echo "You can now connect to the MCP interface at http://localhost:3000"
echo
echo "To check indexing status: curl http://localhost:3000/status"
echo "To stop the service: docker compose down"
echo
echo "Services are running in the background. Happy coding!"