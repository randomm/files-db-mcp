# Project Initialization with Auto-Configuration

Files-DB-MCP includes an automatic project type detection and configuration system that helps optimize the system for different codebases.

## How Project Initialization Works

When Files-DB-MCP starts, it automatically:

1. Detects the type of project based on file patterns and directory structure
2. Selects an appropriate embedding model for the detected project type
3. Auto-configures model settings (device, quantization, normalization)
4. Detects project-specific ignore patterns from .gitignore and .dockerignore
5. Creates a configuration file for future use
6. Starts indexing with optimized settings

This zero-configuration approach means that Files-DB-MCP works out-of-the-box for most projects without manual setup.

## Supported Project Types

The system can detect and optimize for various project types, including:

- **Python** - Detected by: pyproject.toml, setup.py, requirements.txt, \_\_init\_\_.py
- **JavaScript** - Detected by: package.json, package-lock.json, yarn.lock
- **TypeScript** - Detected by: tsconfig.json, tsc.config, index.ts
- **Go** - Detected by: go.mod, go.sum, main.go
- **Rust** - Detected by: Cargo.toml, Cargo.lock, src/main.rs
- **Java** - Detected by: pom.xml, build.gradle, settings.gradle
- **C/C++** - Detected by: CMakeLists.txt, Makefile, .cpp, .hpp, .c, .h
- **C#** - Detected by: .csproj, .sln, Program.cs
- **PHP** - Detected by: composer.json, composer.lock, artisan
- **Ruby** - Detected by: Gemfile, Rakefile, .ruby-version

For each project type, Files-DB-MCP applies specialized settings for optimal performance.

## Smart Defaults

### Embedding Models

Project type-specific embedding models are automatically selected:

| Project Type | Default Embedding Model |
|--------------|-------------------------|
| Python, JavaScript, TypeScript | `jinaai/jina-embeddings-v2-base-code` |
| Go, Rust, C/C++ | `Salesforce/SFR-Embedding-2_R` |
| Java, C# | `Alibaba-NLP/gte-large-en-v1.5` |
| PHP, Ruby | `BAAI/bge-large-en-v1.5` |
| Default | `sentence-transformers/all-MiniLM-L6-v2` |

### Model Configuration

The system automatically configures:

- **Device Selection**: Automatically detects and uses GPU if available (CUDA or Apple Silicon MPS)
- **Quantization**: Applies 8-bit quantization by default for most models to reduce memory usage
- **Normalization**: Enables embedding normalization for better search results
- **Prompt Templates**: Uses code-specific prompt templates for improved code understanding

### Project-Specific Ignore Patterns

Automatically detects and respects patterns from:

- `.gitignore` files
- `.dockerignore` files

Additionally, applies language-specific ignore patterns for each project type, such as:

- Python: venv/, \_\_pycache\_\_/, *.pyc
- JavaScript/TypeScript: node_modules/, dist/, .next/
- Go: vendor/, bin/
- Rust: target/, debug/
- Java: target/, build/, *.class

## Manual Configuration

You can override the automatic configuration using command-line arguments:

```bash
python -m src.main --embedding-model "your-preferred-model" --model-config '{"device": "cpu"}'
```

To disable auto-configuration completely:

```bash
python -m src.main --disable-auto-config
```

## MCP Interface

The MCP interface provides several commands for working with project configuration:

### Get Project Configuration

```json
{
  "function": "get_project_config",
  "request_id": "123"
}
```

### Detect Project Type

```json
{
  "function": "detect_project_type",
  "parameters": {
    "force_redetect": true
  },
  "request_id": "123"
}
```

### Update Project Configuration

```json
{
  "function": "update_project_config",
  "parameters": {
    "embedding_model": "BAAI/bge-large-en-v1.5",
    "model_config": {
      "device": "cuda",
      "normalize_embeddings": true
    },
    "custom_ignore_patterns": ["*.log", "temp/"]
  },
  "request_id": "123"
}
```

## Configuration File

The system stores configuration in a JSON file at `.files-db-mcp/config.json` with the following structure:

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

## Performance Considerations

- **Model Selection**: Code-specific models provide better results but may be larger and slower
- **Device Selection**: GPU acceleration provides significant speed improvements when available
- **Quantization**: 8-bit quantization reduces memory usage with minimal impact on accuracy
- **Incremental Indexing**: After changing models, a full re-indexing is performed automatically