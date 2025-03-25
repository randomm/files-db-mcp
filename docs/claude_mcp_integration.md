# Claude Code MCP Integration

Files-DB-MCP now integrates directly with Claude Code via the Model Context Protocol (MCP), allowing AI assistants to search your codebase directly without manual interaction.

## Overview

The Model Context Protocol (MCP) enables standardized communication between AI models like Claude and external tools. With this integration, Claude can:

1. Search your codebase using semantic vector search
2. Retrieve file contents directly
3. Get information about the embeddings model

This makes Claude significantly more effective at understanding and working with your codebase.

### Architecture

The Files-DB-MCP system consists of two main components:

1. **Vector Database (Qdrant)**: Stores and indexes the embeddings of your code files
2. **MCP Interface Service**: Processes files, generates embeddings, and exposes an API for Claude

When integrated with Claude, the architecture works like this:

```
Claude Code CLI/Desktop → MCP Server (port 3000) → Vector Database (port 6333)
```

The Claude MCP client never connects directly to the vector database - it always communicates through our MCP interface service running on port 3000.

## Setting Up the Integration

### Prerequisites

- Files-DB-MCP Docker environment set up and running
- Claude Desktop or Claude Code CLI installed

### Claude Desktop Configuration

Add the following to your `claude_desktop_config.json` file:

```json
{
  "mcpServers": {
    "files-db-mcp": {
      "command": "python",
      "args": ["/path/to/src/claude_mcp_server.py", "--host", "localhost", "--port", "3000"]
    }
  }
}
```

Note that we connect to port 3000, which is the MCP interface port that's exposed by our Docker container.

### Claude Code CLI Configuration

If you're using Claude Code CLI, add the following to your configuration:

```json
{
  "mcpTools": [
    {
      "name": "files-db-mcp",
      "command": "python /path/to/src/claude_mcp_server.py --host localhost --port 3000"
    }
  ]
}
```

For installations using the default setup script, you can use:

```json
{
  "mcpTools": [
    {
      "name": "files-db-mcp",
      "command": "python ~/.files-db-mcp/src/claude_mcp_server.py --host localhost --port 3000"
    }
  ]
}
```

Or if you're using a `.mcp.json` file in your project root:

```json
{
  "mcpServers": {
    "files-db-mcp": {
      "type": "stdio",
      "command": "python",
      "args": [
        "~/.files-db-mcp/src/claude_mcp_server.py",
        "--host",
        "localhost",
        "--port",
        "3000"
      ],
      "env": {}
    }
  }
}
```

**Important:** Make sure to use the full path to the `src/claude_mcp_server.py` file. The file is located in the `src` subdirectory, not directly in the `~/.files-db-mcp` directory.

## Using the Integration

After setting up the integration, start a new conversation with Claude and enable the Files-DB-MCP MCP tool.

### Example Queries

Here are some examples of how to interact with the MCP integration:

1. **Find relevant files**: "Search my codebase for files related to database connections"

2. **Get specific implementation details**: "Find the API endpoint implementation for user authentication"

3. **Explore project structure**: "Help me understand the overall architecture of this project"

### Available Functions

The integration exposes the following functions to Claude:

#### vector_search

Searches your codebase using semantic similarity:

```json
{
  "query": "database connection",
  "limit": 5,
  "file_extensions": ["py", "js"],
  "path_prefix": "src/",
  "threshold": 0.7
}
```

#### get_file_content

Retrieves the full content of a specific file:

```json
{
  "file_path": "src/database.py"
}
```

#### get_model_info

Returns information about the current embedding model:

```json
{}
```

## Troubleshooting

### Architecture and Port Configuration

Understanding the architecture and port configuration is important for troubleshooting:

- **Vector Database (Qdrant)**: Runs on port 6333 inside the container, mapped to host port 6333
- **MCP Interface**: Runs on port 8000 inside the container, mapped to host port 3000
- **Claude MCP Client**: Connects to the MCP Interface on port 3000, not directly to the vector database

### Common Issues

1. **"Connection closed" error**: 
   - Make sure you're connecting to port 3000 (not 6333)
   - Check if Files-DB-MCP is running with `docker ps`
   - Verify the MCP interface is healthy with `curl http://localhost:3000/health`

2. **Connection refused error**: 
   - Make sure Files-DB-MCP is running and the ports are correctly mapped
   - Check if there's a port conflict on your system

3. **Tool not showing up in Claude**: 
   - Restart Claude Desktop/CLI after modifying the MCP configuration
   - Make sure you've enabled the tool in your Claude session

4. **Search returning no results**: 
   - Ensure your codebase has been properly indexed
   - Check indexing status with `curl http://localhost:3000/health`
   - Verify the project path in your docker-compose configuration
   
5. **"Connection closed" or "MCP error -32000: Connection closed"**:
   - Verify the path to `claude_mcp_server.py` in your MCP configuration
   - Make sure to specify the full path including the `src` directory: `~/.files-db-mcp/src/claude_mcp_server.py`
   - Check if the file exists using `ls -la ~/.files-db-mcp/src/claude_mcp_server.py`
   - Try running the command manually to see if it works: `python ~/.files-db-mcp/src/claude_mcp_server.py --host localhost --port 3000`

### Logs and Diagnostics

For troubleshooting, check these logs:

- Files-DB-MCP service logs: `docker logs files-db-mcp-files-db-mcp-1`
- Vector database logs: `docker logs files-db-mcp-vector-db-1`
- Overall system logs: `docker-compose logs`
- Check Claude MCP status: `claude --mcp-debug`

You can also test the MCP connection directly:

```bash
# Test health endpoint
curl http://localhost:3000/health

# Test search functionality directly
curl -X POST http://localhost:3000/mcp -H "Content-Type: application/json" -d '{"function":"vector_search","parameters":{"query":"test","limit":5}}'
```

## Future Improvements

- Support for more advanced search parameters
- Direct code editing capabilities
- Integration with other IDEs and development tools

## Contributing

Contributions to improve the MCP integration are welcome! See our contribution guidelines for more information.