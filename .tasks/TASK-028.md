# TASK-028: Optimize file indexing performance

## Priority: High

## Status: To Do

## Description
Current file indexing performance is extremely slow, taking approximately 30 seconds to index just 12 files (2.5 seconds per file). This will result in unacceptable performance for larger codebases. We need to investigate performance optimizations to dramatically improve indexing speed.

There's an alternative implementation at https://github.com/randomm/local-indexing-mcp that reportedly achieves much faster indexing. We should study its approach and integrate the best practices into our system.

## Requirements
- Analyze indexing bottlenecks (file processing, embedding generation, database operations)
- Study the referenced alternative implementation for performance techniques
- Implement parallel processing for file indexing where appropriate
- Optimize database operations (batch inserts, connection pooling)
- Benchmark performance improvements with various codebase sizes

## Implementation Details
1. Profile current indexing implementation to identify slowest components
2. Review the alternative implementation's approach to file processing
3. Implement parallel file processing and embedding generation
4. Add batching for vector database operations
5. Consider implementing incremental indexing for changed files only
6. Optimize SentenceTransformer settings for faster inference

## Acceptance Criteria
- At least 10x improvement in indexing speed
- Ability to handle large codebases (10,000+ files) in a reasonable time
- Clear performance metrics documented for different codebase sizes
- Minimal memory overhead for parallel processing

## Related Files
- `/src/file_processor.py`
- `/src/vector_search.py`
- `/src/main.py`

## Notes
The target index speed should be at least 10 files per second on average hardware. The alternative implementation may use different embedding techniques or optimizations for the vector database that we can adopt.