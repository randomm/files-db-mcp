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
echo "Note: First run requires downloading embedding models (~300-500MB) which may take several minutes."
echo "      Future startups will be much faster as models are cached."

# Get the actual container names as they might be different
MCP_CONTAINER=$(docker compose -f "$BASE_DIR/docker-compose.yml" ps -q files-db-mcp)
VECTOR_DB_CONTAINER=$(docker compose -f "$BASE_DIR/docker-compose.yml" ps -q vector-db)

echo "Container IDs: MCP=$MCP_CONTAINER, Vector DB=$VECTOR_DB_CONTAINER"

# Wait up to 10 minutes for MCP to become healthy (model downloads can take time)
timeout=600
interval=10
elapsed=0

echo "Waiting for MCP service to become healthy..."
previous_status=""
previous_logs=""
no_progress_count=0

while [ $elapsed -lt $timeout ]; do
    # Check if files-db-mcp is healthy
    if [ ! -z "$MCP_CONTAINER" ]; then
        MCP_STATUS=$(docker inspect --format='{{if .State.Health}}{{.State.Health.Status}}{{else}}no health check{{end}}' "$MCP_CONTAINER" 2>/dev/null || echo "error")
        
        # Get the latest logs for analysis
        RECENT_LOGS=$(docker logs --tail 50 "$MCP_CONTAINER" 2>&1)
        
        # Extract key information
        MODEL_DOWNLOAD=$(echo "$RECENT_LOGS" | grep -E "Downloading|Loading embedding model|Progress:" | tail -n 3)
        ERROR_LOGS=$(echo "$RECENT_LOGS" | grep -E "Error|Exception|Failed|WARNING" | tail -n 3)
        INDEXING_PROGRESS=$(echo "$RECENT_LOGS" | grep -E "Indexed|Processing files|file_processor" | tail -n 2)
        
        # Only print status if it changed or we have new logs to show
        if [ "$MCP_STATUS" != "$previous_status" ] || [ "$MODEL_DOWNLOAD" != "$previous_logs" ]; then
            # Display a nice timestamp and status
            echo -e "\n[$(date +"%H:%M:%S")] MCP Status: $MCP_STATUS"
            
            # Show relevant progress information based on what we find in logs
            if [ ! -z "$MODEL_DOWNLOAD" ]; then
                echo -e "\n📥 Model download progress:"
                echo "$MODEL_DOWNLOAD" | sed 's/^/  /'
                previous_logs="$MODEL_DOWNLOAD"
                no_progress_count=0
            elif [ ! -z "$INDEXING_PROGRESS" ]; then
                echo -e "\n📊 Indexing progress:"
                echo "$INDEXING_PROGRESS" | sed 's/^/  /'
                previous_logs="$INDEXING_PROGRESS"
                no_progress_count=0
            elif [ ! -z "$ERROR_LOGS" ]; then
                echo -e "\n⚠️ Recent issues detected:"
                echo "$ERROR_LOGS" | sed 's/^/  /'
                previous_logs="$ERROR_LOGS"
                no_progress_count=0
            else
                # If we have no specific progress to show, but status changed
                if [ "$MCP_STATUS" != "$previous_status" ]; then
                    echo "  System is initializing..."
                    no_progress_count=0
                else
                    # Increment the counter if we've shown this before
                    no_progress_count=$((no_progress_count + 1))
                    
                    # Every 3 iterations with no change, show a waiting message
                    if [ $((no_progress_count % 3)) -eq 0 ]; then
                        echo "  Still working... (elapsed: ${elapsed}s)"
                        
                        # After 60 seconds with no progress, show a more detailed message
                        if [ $elapsed -gt 60 ]; then
                            echo "  Taking longer than expected. For detailed logs run:"
                            echo "  docker logs $MCP_CONTAINER"
                        fi
                    fi
                fi
            fi
            
            previous_status="$MCP_STATUS"
        fi
        
        # If healthy, we're done
        if [ "$MCP_STATUS" = "healthy" ]; then
            echo -e "\n✅ MCP service is healthy!"
            break
        fi
    else
        echo "❌ MCP container not found!"
        sleep 5
        # Try to find the container again
        MCP_CONTAINER=$(docker compose -f "$BASE_DIR/docker-compose.yml" ps -q files-db-mcp)
    fi
    
    sleep $interval
    elapsed=$((elapsed + interval))
done

if [ $elapsed -ge $timeout ]; then
    echo -e "\n⏱️ Timeout waiting for MCP service to become healthy after ${timeout} seconds."
    echo -e "\n🔍 Diagnostic information:"
    
    # Get the latest error logs
    echo -e "\nLast few errors from MCP container:"
    docker logs "$MCP_CONTAINER" 2>&1 | grep -E "ERROR|Error|Exception|Failed" | tail -n 5 | sed 's/^/  /'
    
    echo -e "\n⚠️ The system failed to initialize properly. This could be due to:"
    echo "  • Network connectivity issues when downloading models"
    echo "  • Insufficient disk space for the model cache"
    echo "  • Incompatible versions of dependencies"
    echo "  • Memory constraints when loading large models"
    
    echo -e "\n📋 Troubleshooting steps:"
    echo "  1. Check full container logs:"
    echo "     docker logs $MCP_CONTAINER"
    echo "     docker logs $VECTOR_DB_CONTAINER"
    echo "  2. Try restarting with:"
    echo "     docker compose -f \"$BASE_DIR/docker-compose.yml\" restart"
    echo "  3. Check for disk space issues:"
    echo "     df -h"
    echo "  4. For detailed troubleshooting help, see the docs at:"
    echo "     https://github.com/randomm/files-db-mcp/blob/main/docs/troubleshooting.md"
    
    exit 1
fi

echo -e "\n🚀 Files-DB-MCP is ready!"

# Get indexing status
HEALTH_INFO=$(curl -s http://localhost:3000/health 2>/dev/null || echo '{"indexed_files":0,"total_files":0,"indexing_progress":0}')
INDEXED_FILES=$(echo $HEALTH_INFO | grep -o '"indexed_files":[0-9]*' | cut -d':' -f2)
TOTAL_FILES=$(echo $HEALTH_INFO | grep -o '"total_files":[0-9]*' | cut -d':' -f2)
PROGRESS=$(echo $HEALTH_INFO | grep -o '"indexing_progress":[0-9.]*' | cut -d':' -f2)

# Display information about indexing status
if [ ! -z "$INDEXED_FILES" ] && [ ! -z "$TOTAL_FILES" ] && [ ! -z "$PROGRESS" ]; then
    echo -e "📊 Indexing status: ${PROGRESS}% complete (${INDEXED_FILES}/${TOTAL_FILES} files)"
    echo -e "   Indexing is running in the background and will continue automatically.\n"
else
    echo -e "📊 Indexing is running in the background and will continue automatically.\n"
fi

echo -e "🔗 Connection Information:"
echo -e "   MCP interface: http://localhost:3000"
echo -e "   Vector database: localhost:6333\n"

echo -e "📝 Useful commands:"
echo -e "   Check indexing status: curl http://localhost:3000/health"
echo -e "   View logs: docker logs $MCP_CONTAINER"
echo -e "   Stop service: docker compose -f \"$BASE_DIR/docker-compose.yml\" down\n"

echo -e "✨ Services are running in the background. Happy coding!"