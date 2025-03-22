# Files-DB-MCP: Architecture Overview

## System Purpose

Files-DB-MCP is a local vector database system designed to provide LLM coding agents with fast, efficient search capabilities for software project files. Instead of traditional grep/glob searching, it enables semantic understanding and retrieval of code through vector embeddings, all accessible via the Message Control Protocol (MCP). The system focuses on zero-configuration deployment to any existing project, with a single command startup that immediately begins indexing and providing search capabilities with progressive improvement.

## High-Level Architecture

```
┌─────────────────┐     ┌─────────────────────┐     ┌───────────────────┐
│                 │     │                     │     │                   │
│  Client Tools   │◄────┤    MCP Interface    │◄────┤   Vector Search   │
│ (Claude Code,   │     │ (stdio/SSE Handler) │     │      Engine       │
│  Cursor, etc.)  │     │                     │     │                   │
└─────────────────┘     └─────────────────────┘     └─────────┬─────────┘
                                                              │
                                                              │
                        ┌─────────────────────┐     ┌─────────▼─────────┐
                        │                     │     │                   │
                        │   File Processor    │────►│   Vector Database │
                        │ (Indexer/Chunker)   │     │                   │
                        │                     │     │                   │
                        └─────────────────────┘     └───────────────────┘
```

## Core Components

### 1. MCP Interface

Responsible for communication with client tools using the Message Control Protocol.

**Key Functions:**
- Parse incoming MCP messages from clients
- Route queries to the vector search engine
- Format search results as MCP responses
- Handle both stdio and SSE communication modes
- Manage connection lifecycle and error handling

**Technologies:**
- Python with standard libraries for stdio handling
- FastAPI or similar for SSE endpoints (if needed)
- JSON for message formatting

### 2. File Processor

Handles scanning, parsing, and embedding generation for project files.

**Key Functions:**
- Automatically start scanning project directories on container launch
- Recursively traverse files with smart exclusions (.git, node_modules, etc.)
- Continuously monitor the file system for new, modified, and deleted files
- Perform real-time incremental updates to the index when files change
- Parse different file types appropriately
- Chunk files into appropriate segments
- Generate embeddings for file chunks using open source models
- Store file metadata and embeddings in the database
- Detect file changes for immediate incremental updates
- Provide immediate search capabilities while indexing continues in background

**Technologies:**
- Python for file operations
- Language-specific parsers for code understanding
- Open source embedding models from Hugging Face optimized for code
- Sentence Transformers with quantization and binary embedding support
- Configurable model selection and embedding parameters

### 3. Vector Search Engine

Core search functionality using vector similarity.

**Key Functions:**
- Convert search queries to embeddings
- Perform vector similarity search
- Filter results based on metadata
- Rank results by relevance
- Format results with file paths and snippets

**Technologies:**
- Vector similarity algorithms (cosine, dot product)
- Query preprocessing techniques
- Relevance scoring mechanisms

### 4. Vector Database

Storage for file embeddings and metadata.

**Key Functions:**
- Store and retrieve vector embeddings
- Maintain file metadata (path, type, modified date)
- Support fast similarity search
- Handle database versioning
- Manage persistence and updates
- Support different embedding formats (full, quantized, binary)

**Technologies:**
- Qdrant, Milvus, or similar vector database
- SQLite for metadata (if needed)
- File-based storage for persistence
- Support for HNSW and other efficient indexing algorithms

## Data Flow

1. **Initial Indexing Process:**
   - File Processor scans project directories immediately on startup
   - Files are parsed and chunked
   - Chunks are converted to embeddings
   - Embeddings and metadata are stored in Vector Database
   - Search becomes available for indexed files while indexing continues

2. **Continuous Monitoring Process:**
   - File system watcher monitors for changes (new, modified, deleted files)
   - Changed files are immediately processed and re-indexed
   - Index is updated in real-time as developers modify their codebase
   - Search results reflect the current state of the project

3. **Search Process:**
   - Client sends query via MCP Interface
   - Query is routed to Vector Search Engine
   - Query is converted to embedding
   - Vector Database performs similarity search
   - Results are ranked and formatted
   - Response is sent back via MCP Interface

## Deployment Architecture

The system is designed to run locally as a Docker-based service with zero configuration required:

```
┌─────────────────────────────────────────────────────────────────┐
│                      Docker Compose Environment                  │
│                                                                 │
│   ┌─────────────────┐        ┌─────────────────┐                │
│   │                 │        │                 │                │
│   │  Main Service   │◄──────►│ Vector Database │                │
│   │ (Auto-starting) │        │                 │                │
│   └────────┬────────┘        └─────────────────┘                │
│            │                                                    │
└────────────┼────────────────────────────────────────────────────┘
             │                      ▲
             │                      │
             │                      │ Single Command
             ▼                      │ Startup
    ┌──────────────────┐     ┌──────────────┐     ┌─────────────┐
    │                  │     │              │     │             │
    │   Client Tools   │     │  Project     │◄────┤  Developer  │
    │                  │     │  Directory   │     │  Workspace  │
    └──────────────────┘     └──────────────┘     └─────────────┘
```

- **One-Command Startup**: Simple CLI command that works in any project directory
- **Main Service Container**: Auto-starting container that runs the MCP Interface, File Processor, and Vector Search Engine
- **Vector Database Container**: Runs the vector database service with automatic initialization
- **Shared Volume**: For persistent storage of embeddings and metadata
- **Project Directory Mounting**: Automatic mounting of project files for indexing
- **Network Bridge**: For communication between containers and LLM tools

## Key Technical Considerations

1. **Performance Optimization**
   - Efficient chunking strategies for different file types
   - Caching mechanisms for frequent queries
   - Incremental indexing to minimize resource usage
   - Query optimization for fast responses
   - Embedding quantization and binary embedding options for space efficiency

2. **Embedding Quality**
   - Selection of appropriate open source models from Hugging Face
   - Configurable embedding parameters and model selection
   - Sentence Transformers with quantization and binary embedding support
   - Chunking strategies that preserve semantic meaning
   - Handling of different programming languages

3. **Scalability**
   - Efficient handling of large codebases
   - Resource usage optimization
   - Pagination for large result sets

4. **Security**
   - Running with appropriate container permissions
   - Avoiding exposure of sensitive code
   - Validation of inputs and paths

5. **Extensibility**
   - Pluggable architecture for embedding models
   - Support for different vector databases
   - Extensible query interface

6. **Zero-Configuration Design**
   - Auto-detection of project structure and languages
   - Smart defaults for different project types
   - Progressive indexing with immediate search availability
   - Continuous file monitoring and real-time index updates
   - Background processing with minimal resource impact
   - One-command startup for any project

## Future Extensions

1. **Advanced Filtering**
   - Language-specific code search
   - Function/class level search
   - Code structure awareness

2. **Integration Options**
   - Support for additional LLM tools
   - IDE plugin support
   - CI/CD integration

3. **Intelligent Indexing**
   - Language-aware parsing
   - Code structure understanding
   - Dependency relationship mapping

4. **Performance Enhancements**
   - Distributed search for very large codebases
   - Optimized embedding models for code
   - Advanced caching strategies