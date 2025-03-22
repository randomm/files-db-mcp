# Files-DB-MCP: Vector Search for Code Projects

Files-DB-MCP is a local vector database system that provides LLM coding agents with fast, efficient search capabilities for software project files. It enables semantic understanding and retrieval of code through vector embeddings, all accessible via the Message Control Protocol (MCP).

## Features

- **One-Command Startup**: Easy to run in any project directory
- **Zero Configuration**: Auto-detects project structure with sensible defaults
- **Real-Time Monitoring**: Continuously watches for file changes and updates the index
- **Vector Search**: Semantic search capabilities for finding relevant code
- **MCP Interface**: Compatible with Claude Code, Cursor, and other LLM tools
- **Direct Claude Code Integration**: MCP implementation for seamless AI interactions
- **Open Source Models**: Uses Hugging Face models for code embeddings
- **Optimization Options**: Supports quantization and binary embeddings

## Quick Start

### One-Line Installation

```bash
curl -fsSL https://raw.githubusercontent.com/yourusername/files-db-mcp/main/install.sh | bash
```

### Usage

After installation, just run in any project directory:

```bash
files-db-mcp
```

That's it! The service will automatically:
1. Detect your project files
2. Start indexing in the background
3. Begin responding to MCP search queries immediately

## Requirements

- Docker
- Docker Compose

## Manual Installation

If you prefer to install manually:

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/files-db-mcp.git
   ```

2. Navigate to a project directory and run:
   ```bash
   /path/to/files-db-mcp/run.sh
   ```

## Configuration (Optional)

Files-DB-MCP works without configuration, but you can customize it by setting environment variables:

- `EMBEDDING_MODEL`: Change the embedding model (default: 'sentence-transformers/all-MiniLM-L6-v2')
- `QUANTIZATION`: Enable/disable quantization (default: 'true')
- `BINARY_EMBEDDINGS`: Enable/disable binary embeddings (default: 'false')
- `IGNORE_PATTERNS`: Comma-separated list of files/dirs to ignore

Example with custom settings:

```bash
EMBEDDING_MODEL=sentence-transformers/code-search-net-base QUANTIZATION=false files-db-mcp
```

## How It Works

1. Files-DB-MCP starts a Docker Compose environment with two services:
   - Vector database (Qdrant)
   - Main service with MCP interface

2. The system immediately begins indexing your project files in the background

3. As you modify files, the index is updated in real-time

4. Your LLM coding tools can search for files using natural language queries

## MCP Interface

Files-DB-MCP implements the Message Control Protocol (MCP) with the following functions:

- `search_files`: Search for files by content similarity
- `get_file_content`: Get the content of a specific file
- `get_model_info`: Get information about the current embedding model

### Claude Code Integration

Files-DB-MCP now includes direct integration with Claude Code via MCP:

```json
{
  "mcpServers": {
    "files-db-mcp": {
      "command": "python",
      "args": ["-m", "src.claude_mcp", "--host", "localhost", "--port", "6333"]
    }
  }
}
```

For detailed setup instructions, see [Claude MCP Integration](docs/claude_mcp_integration.md).

## Status and Monitoring

Check indexing status:

```bash
curl http://localhost:3000/health
```

## Documentation

- [Installation Guide](docs/installation_guide.md) - Detailed installation instructions
- [Docker Setup](docs/docker_setup.md) - Docker Compose setup guide
- [API Reference](docs/api_reference.md) - Complete API documentation
- [Claude MCP Integration](docs/claude_mcp_integration.md) - Claude Code integration
- [Troubleshooting](docs/troubleshooting.md) - Solutions to common issues
- [Model Configuration](docs/model_configuration.md) - Configure embedding models
- [SSE API](docs/sse_api.md) - Real-time updates via Server-Sent Events

## License

[MIT License]

## Contributing

Contributions are welcome! Please feel free to submit a pull request.