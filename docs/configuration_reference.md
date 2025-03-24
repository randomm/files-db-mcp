# Configuration Reference

This document provides a comprehensive reference for all configuration options available in Files-DB-MCP.

## Configuration Methods

Files-DB-MCP can be configured through several methods (in order of precedence):

1. **Command-line arguments**: Highest precedence, overrides other methods
2. **Environment variables**: Applied if command-line arguments are not provided
3. **Configuration file**: Located at `.files-db-mcp/config.json` in the project directory
4. **Auto-detection**: Automatic project type detection with smart defaults
5. **Global defaults**: Applied if no other configuration is available

## Command-Line Arguments

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `--project-path` | string | Current directory | Path to the project directory to index |
| `--data-dir` | string | `.files-db-mcp` in current directory | Directory to store data |
| `--host` | string | `0.0.0.0` | Host to bind to |
| `--port` | integer | `8000` | Port to bind to |
| `--ignore` | string[] | [`.git`, `node_modules`, ...] | Patterns to ignore during indexing |
| `--embedding-model` | string | Auto-detected | Embedding model to use |
| `--model-config` | JSON string | `{}` | JSON with embedding model configuration |
| `--disable-sse` | boolean | `false` | Disable SSE interface |
| `--debug` | boolean | `false` | Enable debug mode |
| `--force-reindex` | boolean | `false` | Force a full re-index of all files |
| `--disable-auto-config` | boolean | `false` | Disable automatic project configuration detection |

**Example:**

```bash
python -m src.main --project-path /path/to/project --port 8001 --embedding-model "Salesforce/SFR-Embedding-2_R" --model-config '{"device": "cuda", "quantization": "int8"}'
```

## Environment Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `PROJECT_PATH` | string | Current directory | Path to the project directory to index |
| `DATA_DIR` | string | `.files-db-mcp` in current directory | Directory to store data |
| `HOST` | string | `0.0.0.0` | Host to bind to |
| `PORT` | integer | `8000` | Port to bind to |
| `EMBEDDING_MODEL` | string | Auto-detected | Embedding model to use |
| `MODEL_CONFIG` | JSON string | `{}` | JSON with embedding model configuration |
| `VECTOR_DB_HOST` | string | `localhost` | Vector database host |
| `VECTOR_DB_PORT` | integer | `6333` | Vector database port |
| `DEBUG` | boolean | `false` | Enable debug mode |

**Example:**

```bash
export EMBEDDING_MODEL="Salesforce/SFR-Embedding-2_R"
export MODEL_CONFIG='{"device": "cuda", "quantization": "int8"}'
export PORT=8001
python -m src.main
```

## Configuration File

The configuration file is automatically generated during project initialization and stored at `.files-db-mcp/config.json`. You can modify this file to customize the configuration.

**Example:**

```json
{
  "project_type": "python",
  "detected_project_types": ["python", "javascript"],
  "embedding_model": "jinaai/jina-embeddings-v2-base-code",
  "model_config": {
    "device": "cuda",
    "normalize_embeddings": true,
    "quantization": "int8",
    "prompt_template": "Code: {text}"
  },
  "custom_ignore_patterns": ["logs/", "*.cache"],
  "auto_generated": true,
  "version": "0.1.0"
}
```

## Automatic Project Type Detection

Files-DB-MCP automatically detects the project type based on file patterns and directory structure. This detection is used to select appropriate default settings.

See [Project Initialization](./project_initialization.md) for details on auto-detection.

## Configuration Categories

### 1. Server Configuration

Controls the HTTP server and API endpoints.

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `host` | string | `0.0.0.0` | Host to bind to |
| `port` | integer | `8000` | Port to bind to |
| `disable_sse` | boolean | `false` | Disable Server-Sent Events interface |
| `debug` | boolean | `false` | Enable debug logging |

### 2. Project Configuration

Controls the project indexing behavior.

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `project_path` | string | Current directory | Path to the project directory to index |
| `data_dir` | string | `.files-db-mcp` in current directory | Directory to store data |
| `ignore_patterns` | string[] | [`.git`, `node_modules`, ...] | Patterns to ignore during indexing |
| `force_reindex` | boolean | `false` | Force a full re-index of all files |
| `disable_auto_config` | boolean | `false` | Disable automatic project configuration detection |

### 3. Vector Database Configuration

Controls the vector database connection and behavior.

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `vector_db_host` | string | `localhost` | Vector database host |
| `vector_db_port` | integer | `6333` | Vector database port |
| `collection_name` | string | `files` | Collection name in the vector database |

### 4. Model Configuration

Controls the embedding model behavior. See [Model Configuration](./model_configuration.md) for details.

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `embedding_model` | string | Depends on project type | Embedding model to use |
| `device` | string | Auto-detected | Device to run the model on (`cpu`, `cuda`, `mps`) |
| `normalize_embeddings` | boolean | `true` | Whether to normalize embeddings |
| `prompt_template` | string | Model-dependent | Template for formatting text before embedding |
| `quantization` | string | `int8` | Quantization type (`int8`, `int4`, `null`) |
| `binary_embeddings` | boolean | `false` | Whether to use binary embeddings |

## MCP Configuration API

The MCP interface provides functions for managing configuration:

### Get Project Configuration

```json
{
  "function": "get_project_config"
}
```

Response:
```json
{
  "success": true,
  "config": {
    "project_type": "python",
    "detected_project_types": ["python", "javascript"],
    "embedding_model": "jinaai/jina-embeddings-v2-base-code",
    "model_config": {
      "device": "cuda",
      "normalize_embeddings": true,
      "quantization": "int8"
    }
  }
}
```

### Detect Project Type

```json
{
  "function": "detect_project_type",
  "parameters": {
    "force_redetect": true
  }
}
```

### Update Project Configuration

```json
{
  "function": "update_project_config",
  "parameters": {
    "embedding_model": "Salesforce/SFR-Embedding-2_R",
    "model_config": {
      "device": "cuda",
      "normalize_embeddings": true
    },
    "custom_ignore_patterns": ["*.log", "temp/"]
  }
}
```

## Docker Environment Variables

When running in Docker, additional environment variables are available:

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `VECTOR_DB_HOST` | string | `vector-db` | Vector database host within Docker network |
| `VECTOR_DB_PORT` | integer | `6333` | Vector database port |
| `PROJECT_MOUNT` | string | `/project` | Mount point for the project directory |
| `DATA_MOUNT` | string | `/data` | Mount point for the data directory |

## Configuration Best Practices

1. **Use Project-Specific Configuration Files**: Let Files-DB-MCP detect your project type and create a configuration file. Make targeted edits to this file rather than using command-line arguments for recurring configuration.

2. **Environment-Specific Configuration**: Use environment variables for settings that change between environments (development, CI/CD, production).

3. **Ignore Patterns**: Keep ignore patterns minimal to avoid excluding important files. The auto-detected patterns from `.gitignore` are usually sufficient.

4. **Model Selection**: Choose models appropriate for your project type and size:
   - For small projects: `BAAI/bge-small-en-v1.5` or `sentence-transformers/all-MiniLM-L6-v2`
   - For medium projects: `jinaai/jina-embeddings-v2-base-code`
   - For large projects with high accuracy needs: `Salesforce/SFR-Embedding-2_R`

5. **Resource Constraints**: Use quantization and CPU mode for environments with limited resources.