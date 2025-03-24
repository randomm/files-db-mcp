# Files-DB-MCP Troubleshooting Guide

This guide helps you diagnose and solve common issues with Files-DB-MCP.

## Table of Contents

1. [Startup Issues](#startup-issues)
2. [Docker Compose Issues](#docker-compose-issues)
3. [Connection Issues](#connection-issues)
4. [Search and Indexing Issues](#search-and-indexing-issues)
5. [Performance Issues](#performance-issues)
6. [MCP Integration Issues](#mcp-integration-issues)
7. [Common Error Messages](#common-error-messages)

## Startup Issues

### Service Fails to Start

**Symptoms:** 
- Service doesn't respond on expected port
- Docker container exits immediately
- Error logs show startup failures

**Check:**
1. **Logs:** Examine startup logs
   ```bash
   docker-compose logs files-db-mcp
   ```

2. **Port Conflicts:** Check if another service is using the same port
   ```bash
   netstat -tuln | grep 3000
   ```

3. **Dependencies:** Verify vector database is running
   ```bash
   docker-compose ps vector-db
   ```

**Solutions:**
- Change the port mapping in `docker-compose.yml` if ports are in use
- Ensure vector database is running and accessible
- Check environment variables are properly set

### Health Check Fails or Long Startup Time

**Symptoms:**
- Container shows "unhealthy" status or "starting" for a long time
- Timeout message: "Timeout waiting for MCP service to become healthy"
- First run takes much longer than expected

**Causes:**
- First startup requires downloading large embedding models (300-500MB)
- Default timeout may be too short for large model downloads
- Slow internet connection can extend download time

**Check:**
1. **Container Logs for Download Progress:**
   ```bash
   docker logs files-db-mcp-files-db-mcp-1
   ```
   Look for "Downloading model.safetensors" progress messages.

2. **Health Check Response:**
   ```bash
   curl http://localhost:3000/health
   ```

3. **Health Check Configuration:** Check the health check timeout in `docker-compose.yml`

**Solutions:**
- Be patient during first startup - subsequent starts will be much faster thanks to model caching
- Increase health check start_period in docker-compose.yml to 600s or more
- Increase timeout in scripts/run.sh to 600 seconds or more
- Switch to a smaller embedding model by setting EMBEDDING_MODEL environment variable
- Check that you have the `model_cache` volume created: `docker volume ls | grep model_cache`

## Docker Compose Issues

### Container Dependency Errors

**Symptoms:**
- `files-db-mcp` service starts before `vector-db` is ready
- "Connection refused" errors in logs

**Solutions:**
- Use `depends_on` with `condition: service_started` in `docker-compose.yml`
- Add retry logic for vector database connections
- Increase startup timeout settings

### Volume Mounting Issues

**Symptoms:**
- Can't find project files
- Permission errors accessing mounted directories

**Solutions:**
- Check volume mount syntax in `docker-compose.yml`
- Ensure proper permissions on host directories
- Use absolute paths for volume mounts

### Python Package Issues

**Symptoms:**
- ImportError for missing packages
- Version compatibility errors

**Solutions:**
- Pin specific versions in `requirements.txt`
- Add specific compatibility requirements (e.g., `huggingface-hub==0.16.4`)
- Rebuild the Docker image with `docker-compose build --no-cache`

## Connection Issues

### Can't Connect to Vector Database

**Symptoms:**
- Error logs showing connection failures
- "Connection refused" errors when starting search

**Check:**
1. **Vector DB Status:**
   ```bash
   docker-compose ps vector-db
   ```

2. **Vector DB Logs:**
   ```bash
   docker-compose logs vector-db
   ```

3. **Network Configuration:**
   ```bash
   docker network inspect files-db-mcp_default
   ```

**Solutions:**
- Ensure correct hostname (`vector-db` inside Docker network)
- Verify port settings (`6333` by default)
- Add connection retry logic with exponential backoff

### API Endpoint Not Responding

**Symptoms:**
- HTTP 404 when accessing endpoints
- Timeout when connecting to service

**Check:**
1. **Service Running:**
   ```bash
   docker-compose ps files-db-mcp
   ```

2. **Port Mapping:**
   ```bash
   docker-compose port files-db-mcp 8000
   ```

**Solutions:**
- Ensure service is running with correct port mapping
- Check for URL path typos (e.g., `/mcp` vs `/api/mcp`)
- Verify service is binding to the correct address (`0.0.0.0` for Docker)

### Model Cache Issues

**Symptoms:**
- Models are re-downloaded every time the container starts
- Long startup times on every run, not just the first time
- Error message about model cache volume 

**Check:**
1. **Docker Volumes:**
   ```bash
   docker volume ls | grep model_cache
   ```

2. **Cache Content:**
   ```bash
   # Run this command to check what's in the cache
   docker run --rm -v model_cache:/cache alpine ls -la /cache
   ```

3. **Cache Size:**
   ```bash
   docker system df -v | grep model_cache
   ```

**Solutions:**
- Ensure the `model_cache` volume exists (it should be created automatically)
- If the volume is missing or corrupted, you can recreate it: `docker volume create model_cache`
- Make sure your docker-compose.yml includes the volume configuration
- For persistent caching across container rebuilds, ensure the cache volume is not being pruned

## Search and Indexing Issues

### No Search Results

**Symptoms:**
- Empty results from search queries
- Low or zero indexing progress

**Check:**
1. **Indexing Status:**
   ```bash
   curl http://localhost:3000/health
   ```

2. **Collection Status:**
   ```bash
   # Create a script to check collection status
   cat > check_collection.py << 'EOF'
   import requests
   response = requests.post(
       "http://localhost:3000/mcp",
       json={"function": "get_model_info", "parameters": {}}
   )
   print(response.json())
   EOF
   python check_collection.py
   ```

**Solutions:**
- Wait for indexing to complete (initial indexing takes time)
- Check if project directory is correctly mounted
- Verify file patterns aren't excluding all files
- Try a broader search query or lower similarity threshold

### Slow Indexing

**Symptoms:**
- Indexing progress is very slow
- High CPU/memory usage during indexing

**Solutions:**
- Tune embedding model (use smaller models for faster processing)
- Enable quantization for faster processing
- Consider binary embeddings for large codebases
- Exclude large unnecessary directories (node_modules, .git, etc.)

## Performance Issues

### High Memory Usage

**Symptoms:**
- Docker container using excessive memory
- OOM (Out of Memory) errors

**Solutions:**
- Enable model quantization to reduce memory footprint
- Configure memory limits in Docker Compose
- Use a smaller embedding model dimension
- Add swap space to host machine

### Slow Search Response

**Symptoms:**
- Search queries take more than 500ms
- High CPU usage during searches

**Solutions:**
- Tune vector database parameters in `vector_search.py`
- Use approximate nearest neighbor search
- Enable caching for frequent queries
- Use binary embeddings for faster distance calculation

## MCP Integration Issues

### Claude Code MCP Connection Failures

**Symptoms:**
- Claude Code can't connect to the MCP server
- Connection timeout errors

**Check:**
1. **MCP Configuration:**
   - Check claude_desktop_config.json
   - Verify path to Python executable

2. **MCP Server Logs:**
   - Run with DEBUG logging
   - Check ~/.files-db-mcp/claude_mcp.log

**Solutions:**
- Ensure files-db-mcp is running and accessible
- Use absolute paths in configuration
- Check port forwarding if running in Docker
- Ensure proper protocol implementation

### Protocol Errors

**Symptoms:**
- Invalid message format errors
- MCP client disconnects unexpectedly

**Solutions:**
- Follow the MCP specification exactly
- Handle all required message types
- Properly format tool results with correct content types
- Set up proper error handling for MCP messages

## Common Error Messages

### "open /Users/janni/.files-db-mcp/scripts/docker-compose.yml: no such file or directory"

**Cause:** Path issue in the installation script after repository reorganization

**Solution:**
- Update to the latest version of Files-DB-MCP
- If issue persists, manually copy docker-compose.yml to the scripts directory:
  ```bash
  cp ~/.files-db-mcp/docker-compose.yml ~/.files-db-mcp/scripts/
  ```

### "ImportError: cannot import name 'cached_download' from 'huggingface_hub'"

**Cause:** Version incompatibility between sentence-transformers and huggingface-hub

**Solution:**
```bash
pip install huggingface-hub==0.16.4
```

### "Connection refused to vector-db:6333"

**Cause:** Vector database service not started or not accessible

**Solution:**
- Ensure vector-db service is running
- Check network configuration
- Add connection retry logic

### "File not found: /project/..."

**Cause:** Incorrect project directory mounting

**Solution:**
- Check volume mount in docker-compose.yml
- Use absolute path for PROJECT_DIR environment variable

### "HealthCheck failed, container exited"

**Cause:** Health check timeout too short or service startup error

**Solution:**
- Increase health check timeout and start period
- Check for startup errors in logs
- Fix any dependency issues

### "CUDA not available, falling back to CPU"

**Cause:** Not a critical error, just informational

**Solution:**
- No action needed unless GPU acceleration is required
- If GPU acceleration is needed, install CUDA and PyTorch with CUDA support

## Diagnostic Commands

### Check System Status

```bash
# Check running services
docker-compose ps

# Check service logs
docker-compose logs files-db-mcp

# Check health status
curl http://localhost:3000/health

# Check indexing progress via SSE
curl http://localhost:3000/sse/indexing-progress
```

### Test MCP Interface

```bash
# Test search functionality
cat > test_search.py << 'EOF'
import requests
import json

response = requests.post(
    "http://localhost:3000/mcp",
    json={
        "function": "search_files",
        "parameters": {
            "query": "test query",
            "limit": 5
        },
        "request_id": "test-123"
    }
)
print(json.dumps(response.json(), indent=2))
EOF
python test_search.py
```

## Still Having Issues?

If you're still experiencing problems:

1. Check the [GitHub Issues](https://github.com/randomm/files-db-mcp/issues) for similar reports
2. Enable DEBUG logging in your configuration
3. Create a detailed bug report including:
   - Steps to reproduce
   - Expected behavior
   - Actual behavior
   - System information
   - Docker and Python versions
   - Log output