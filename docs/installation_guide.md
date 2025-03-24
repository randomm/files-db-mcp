# Files-DB-MCP Installation Guide

This guide provides detailed instructions for installing and configuring Files-DB-MCP in various environments.

## Overview

Files-DB-MCP can be installed and run in several ways:

1. **Docker Compose** (recommended) - Run as containerized services
2. **CLI Tool** - Install globally and run as a command-line tool
3. **Manual Installation** - Install and run from source
4. **Development Setup** - Install with additional development dependencies

## Prerequisites

- Python 3.9+ (for non-Docker installations)
- Docker and Docker Compose (for containerized installation)
- Git (for installation from source)
- 1GB+ RAM available (vector embeddings require memory)

## 1. Docker Compose Installation (Recommended)

The Docker Compose installation is the simplest and most reliable way to run Files-DB-MCP.

### Quick Install

```bash
# Clone the repository
git clone https://github.com/randomm/files-db-mcp.git
cd files-db-mcp

# Start the services
docker-compose up -d
```

### Configuration

The Docker Compose setup can be configured through environment variables:

```bash
# Set environment variables
PROJECT_DIR=/path/to/your/project \
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2 \
QUANTIZATION=true \
docker-compose up -d
```

See [Docker Setup Guide](docker_setup.md) for detailed Docker configuration options.

## 2. CLI Tool Installation

Files-DB-MCP can be installed as a global CLI tool for easy access from any project directory.

### Install via pip

```bash
# Install the latest stable version
pip install files-db-mcp

# Or install the development version
pip install git+https://github.com/randomm/files-db-mcp.git
```

### Usage

Once installed, you can run Files-DB-MCP from any project directory:

```bash
# Start Files-DB-MCP in the current directory
files-db-mcp

# Or specify a project directory
files-db-mcp --project-path /path/to/your/project
```

### CLI Options

```
Usage: files-db-mcp [OPTIONS]

Options:
  --project-path TEXT       Path to the project directory
  --data-dir TEXT           Directory to store data
  --host TEXT               Host to bind to
  --port INTEGER            Port to bind to
  --ignore TEXT             Patterns to ignore during indexing
  --embedding-model TEXT    Embedding model to use
  --model-config TEXT       JSON string with embedding model configuration
  --disable-sse             Disable SSE interface
  --debug                   Enable debug mode
  --help                    Show this message and exit
```

## 3. Manual Installation from Source

For advanced users who want to install from source:

```bash
# Clone the repository
git clone https://github.com/randomm/files-db-mcp.git
cd files-db-mcp

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r src/requirements.txt

# Run the application
python -m src.main
```

## 4. Development Setup

For developers who want to contribute to Files-DB-MCP:

```bash
# Clone the repository
git clone https://github.com/randomm/files-db-mcp.git
cd files-db-mcp

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies with development extras
pip install -e ".[dev]"

# Run tests
pytest

# Run linters
black .
isort .
ruff check .
```

## Verifying the Installation

To verify that Files-DB-MCP is running correctly:

1. Check the health endpoint:
   ```bash
   curl http://localhost:3000/health
   ```

2. Search using the MCP interface:
   ```bash
   # Create a test script
   cat > test_mcp.py << 'EOF'
   import requests
   import json

   # Test health endpoint
   health_response = requests.get("http://localhost:3000/health")
   print(f"Health check status: {health_response.status_code}")
   print(f"Health check response: {health_response.json()}\n")

   # Test MCP endpoint
   mcp_request = {
       "function": "search_files",
       "parameters": {
           "query": "example search",
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
   EOF

   # Run the test script
   python test_mcp.py
   ```

## Troubleshooting Installation

### Common Issues

#### Docker Installation Issues

- **Error:** `Cannot connect to the Docker daemon`
  - **Solution:** Ensure Docker is running. Try `docker ps` to verify.

- **Error:** `Ports are already allocated`
  - **Solution:** Change the port mapping in docker-compose.yml or stop any services using ports 3000 and 6333.

#### Python Installation Issues

- **Error:** `SentenceTransformer requires PyTorch`
  - **Solution:** Install PyTorch separately (`pip install torch`) before installing Files-DB-MCP.

- **Error:** `ImportError: cannot import name 'cached_download' from 'huggingface_hub'`
  - **Solution:** Pin the huggingface-hub version: `pip install huggingface-hub==0.16.4`

### Getting Help

If you encounter issues not covered in this guide:

1. Check the [Troubleshooting Guide](troubleshooting.md) for more specific problems
2. Open an issue on GitHub
3. Consult the [FAQ](faq.md) for answers to common questions

## Next Steps

After installation, see these resources:

- [Quick Start Guide](quick_start.md) - Get started with Files-DB-MCP
- [Configuration Reference](configuration.md) - Configure Files-DB-MCP for your needs
- [API Reference](api_reference.md) - Learn about the APIs
- [Claude MCP Integration](claude_mcp_integration.md) - Integrate with Claude Code