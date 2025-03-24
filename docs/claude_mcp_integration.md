# Claude Code MCP Integration

Files-DB-MCP now integrates directly with Claude Code via the Model Context Protocol (MCP), allowing AI assistants to search your codebase directly without manual interaction.

## Overview

The Model Context Protocol (MCP) enables standardized communication between AI models like Claude and external tools. With this integration, Claude can:

1. Search your codebase using semantic vector search
2. Retrieve file contents directly
3. Get information about the embeddings model

This makes Claude significantly more effective at understanding and working with your codebase.

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
      "args": ["/path/to/src/claude_mcp_server.py", "--host", "localhost", "--port", "6333"]
    }
  }
}
```

If you're running Files-DB-MCP in Docker, ensure you map the necessary ports from the container to your host machine.

### Claude Code CLI Configuration

If you're using Claude Code CLI, add the following to your configuration:

```json
{
  "mcpTools": [
    {
      "name": "files-db-mcp",
      "command": "python /path/to/src/claude_mcp_server.py --host localhost --port 6333"
    }
  ]
}
```

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

### Common Issues

1. **Connection refused**: Make sure Files-DB-MCP is running and the ports are correctly mapped

2. **Tool not showing up**: Restart Claude Desktop after modifying the configuration

3. **Search returning no results**: Ensure your codebase has been properly indexed

### Logs

Check the following logs for troubleshooting:

- Files-DB-MCP logs: `docker-compose logs files-db-mcp`
- Claude Desktop logs: Check the Claude Desktop application logs

## Future Improvements

- Support for more advanced search parameters
- Direct code editing capabilities
- Integration with other IDEs and development tools

## Contributing

Contributions to improve the MCP integration are welcome! See our contribution guidelines for more information.