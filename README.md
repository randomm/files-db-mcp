# Files-DB-MCP: Vector Search for Code Projects

A local vector database system that provides LLM coding agents with fast, efficient search capabilities for software projects via the Message Control Protocol (MCP).

## Features

- **Zero Configuration** - Auto-detects project structure with sensible defaults
- **Real-Time Monitoring** - Continuously watches for file changes
- **Vector Search** - Semantic search for finding relevant code
- **MCP Interface** - Compatible with Claude Code and other LLM tools
- **Open Source Models** - Uses Hugging Face models for code embeddings

## Installation

```bash
git clone git@github.com:randomm/files-db-mcp.git ~/.files-db-mcp && bash ~/.files-db-mcp/setup.sh
```

## Usage

After installation, run in any project directory:

```bash
files-db-mcp
```

The service will:
1. Detect your project files
2. Start indexing in the background
3. Begin responding to MCP search queries immediately

## Requirements

- Docker
- Docker Compose

## Configuration

Files-DB-MCP works without configuration, but you can customize it with environment variables:

- `EMBEDDING_MODEL` - Change the embedding model (default: 'sentence-transformers/all-MiniLM-L6-v2')
- `QUANTIZATION` - Enable/disable quantization (default: 'true')
- `BINARY_EMBEDDINGS` - Enable/disable binary embeddings (default: 'false')
- `IGNORE_PATTERNS` - Comma-separated list of files/dirs to ignore

## Claude Code Integration

Add to your Claude Code configuration:

```json
{
  "mcpServers": {
    "files-db-mcp": {
      "command": "python",
      "args": ["/path/to/src/claude_mcp_server.py", "--host", "localhost", "--port", "6333"]
    }
  }
}
```

For details, see [Claude MCP Integration](docs/claude_mcp_integration.md).

## Documentation

- [Installation Guide](docs/installation_guide.md) - Detailed setup instructions
- [API Reference](docs/api_reference.md) - Complete API documentation
- [Configuration Guide](docs/configuration_reference.md) - Configuration options

## Repository Structure

- `/src` - Source code
- `/tests` - Unit and integration tests
- `/docs` - Documentation
- `/scripts` - Utility scripts
- `/install` - Installation scripts
- `/.docker` - Docker configuration
- `/config` - Configuration files
- `/ai-assist` - AI assistance files

## License

[MIT License](LICENSE)

## Contributing

Contributions welcome! Please feel free to submit a pull request.