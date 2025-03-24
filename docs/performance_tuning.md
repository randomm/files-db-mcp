# Performance Tuning Guide

This document provides recommendations for optimizing Files-DB-MCP performance in various environments and scenarios.

## Performance Overview

Files-DB-MCP performance is affected by several key factors:

1. **Embedding Model**: Size and complexity of the embedding model
2. **Hardware Resources**: CPU, GPU, memory availability
3. **Project Size**: Number and size of files being indexed
4. **Indexing Strategy**: Full vs. incremental indexing
5. **Query Complexity**: Number and complexity of search queries
6. **Configuration Settings**: Quantization, device selection, etc.

## Hardware Recommendations

### Minimum Requirements

- **CPU**: 2 cores
- **RAM**: 4GB (8GB recommended)
- **Disk**: 1GB + ~20% of project size
- **Network**: Low latency connection to clients

### Recommended for Large Codebases

- **CPU**: 4+ cores
- **RAM**: 16GB+
- **GPU**: NVIDIA GPU with 4GB+ VRAM or Apple Silicon with 8GB+ unified memory
- **Disk**: SSD with 5GB + ~20% of project size
- **Network**: Gigabit connection

## Embedding Model Selection

Choosing the right embedding model significantly impacts performance:

| Model | Size | Speed | Accuracy | Memory Usage | Recommendation |
|-------|------|-------|----------|--------------|----------------|
| `sentence-transformers/all-MiniLM-L6-v2` | Small | Very Fast | Good | Low | Resource-constrained environments |
| `BAAI/bge-small-en-v1.5` | Small | Fast | Good | Low | Development environments |
| `jinaai/jina-embeddings-v2-base-code` | Medium | Medium | Very Good | Medium | General code search (balanced) |
| `Alibaba-NLP/gte-large-en-v1.5` | Large | Slow | Excellent | High | Multilingual codebases |
| `Salesforce/SFR-Embedding-2_R` | Large | Slow | Superior | High | High-accuracy requirements |

### Performance Impact

| Model | CPU (i7) | GPU (RTX 3060) | Apple M1 |
|-------|----------|----------------|----------|
| Small models | ~200ms/file | ~50ms/file | ~80ms/file |
| Medium models | ~500ms/file | ~120ms/file | ~200ms/file |
| Large models | ~1.2s/file | ~250ms/file | ~400ms/file |

## Optimization Techniques

### 1. GPU Acceleration

Using GPU acceleration can provide 4-10x performance improvement for embedding generation:

```bash
# Enable CUDA for NVIDIA GPUs
python -m src.main --model-config '{"device": "cuda"}'

# Enable MPS for Apple Silicon
python -m src.main --model-config '{"device": "mps"}'
```

### 2. Quantization

Quantization reduces model size and memory usage with minimal accuracy impact:

```bash
# Enable 8-bit quantization (recommended for most cases)
python -m src.main --model-config '{"quantization": "int8"}'

# Enable 4-bit quantization (for extreme memory constraints)
python -m src.main --model-config '{"quantization": "int4"}'
```

Memory usage reduction:
- 8-bit quantization: ~50% reduction
- 4-bit quantization: ~75% reduction

### 3. Incremental Indexing

Incremental indexing significantly improves performance for subsequent runs:

```bash
# Ensure incremental indexing is enabled (default)
python -m src.main

# Force full reindexing when needed
python -m src.main --force-reindex
```

Performance comparison:
- Full indexing: O(n) time complexity
- Incremental indexing: O(m) time complexity, where m is the number of changed files

### 4. Ignore Patterns

Properly configured ignore patterns reduce unnecessary file processing:

```bash
# Add custom ignore patterns
python -m src.main --ignore "*.log" "tmp/*" "build/*"
```

### 5. Search Optimization

Optimize search queries for better performance:

```json
{
  "function": "search_files",
  "parameters": {
    "query": "user authentication function",
    "limit": 5,
    "file_extensions": ["js", "ts"],
    "threshold": 0.7,
    "search_params": {
      "exact": false,
      "hnsw_ef": 128
    }
  }
}
```

| Parameter | Impact | Recommendation |
|-----------|--------|----------------|
| `limit` | Lower limits improve response time | 5-10 for typical searches |
| `threshold` | Higher thresholds reduce results but improve relevance | 0.65-0.75 for balanced performance |
| `file_extensions` | Filtering reduces search space | Always specify when file type is known |
| `hnsw_ef` | Controls search accuracy vs. speed | 64-128 for balanced performance |
| `exact` | Exact search is slower but more accurate | Use `false` for better performance |

## Environment-Specific Tuning

### Docker Environment

In Docker, configure container resources:

```yaml
services:
  files-db-mcp:
    image: files-db-mcp:latest
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
```

### CI/CD Environment

For CI/CD environments where speed is critical:

```bash
python -m src.main \
  --embedding-model "BAAI/bge-small-en-v1.5" \
  --model-config '{"device": "cpu", "quantization": "int8"}' \
  --disable-sse
```

### Development Environment

For development environments where fast startup is desired:

```bash
python -m src.main \
  --embedding-model "jinaai/jina-embeddings-v2-base-code" \
  --model-config '{"device": "auto", "quantization": "int8"}'
```

### Production Environment

For production environments where accuracy is prioritized:

```bash
python -m src.main \
  --embedding-model "Salesforce/SFR-Embedding-2_R" \
  --model-config '{"device": "cuda", "normalize_embeddings": true}'
```

## Benchmarking

You can benchmark your setup using the built-in tools:

```bash
python -m src.tools.benchmark --model "jinaai/jina-embeddings-v2-base-code" --files 1000
```

Typical benchmarks for a medium-sized project (10,000 files):

| Configuration | Initial Indexing | Incremental Update | Search Latency |
|---------------|------------------|-------------------|---------------|
| Small model, CPU | 15-25 minutes | 2-5 seconds/file | 100-300ms |
| Medium model, CPU | 30-45 minutes | 5-10 seconds/file | 200-500ms |
| Medium model, GPU | 8-15 minutes | 1-3 seconds/file | 100-250ms |
| Large model, GPU | 15-30 minutes | 2-5 seconds/file | 150-350ms |

## Memory Usage Optimization

For environments with limited memory:

1. **Use smaller models with quantization**:
   ```bash
   python -m src.main --embedding-model "BAAI/bge-small-en-v1.5" --model-config '{"quantization": "int8"}'
   ```

2. **Process files in smaller batches**:
   Edit `.files-db-mcp/config.json` to add:
   ```json
   "indexing_config": {
     "batch_size": 5,
     "max_workers": 2
   }
   ```

3. **Limit content size**:
   ```json
   "indexing_config": {
     "max_content_chars": 3000
   }
   ```

## Scaling for Large Codebases

For very large codebases (100K+ files):

1. **Use selective indexing**:
   ```bash
   python -m src.main --ignore "test/*" "docs/*" "*.md" "*.txt"
   ```

2. **Distribute across multiple instances**:
   - Instance 1: `python -m src.main --project-path /path/to/project/frontend`
   - Instance 2: `python -m src.main --project-path /path/to/project/backend`

3. **Use vector database persistence**:
   ```bash
   python -m src.main --data-dir "/persistent/storage/.files-db-mcp"
   ```

## Performance Monitoring

Monitor system performance:

```bash
curl http://localhost:8000/metrics
```

Key metrics to monitor:
- Indexing rate (files/second)
- Search latency (ms)
- Memory usage (MB)
- CPU/GPU utilization (%)

## Troubleshooting Performance Issues

### High Memory Usage

1. Check if you're using a large model without quantization
2. Reduce batch size for indexing
3. Use a smaller model with quantization

### Slow Indexing

1. Check hardware resources (CPU/GPU utilization)
2. Verify ignore patterns to exclude unnecessary files
3. Consider using a smaller embedding model
4. Enable GPU acceleration if available

### Slow Search Performance

1. Add more specific filters to your queries
2. Reduce the value of `hnsw_ef` in search parameters
3. Use a lower search result limit
4. Consider increasing the similarity threshold

### High CPU/GPU Usage

1. Limit the number of concurrent searches
2. Adjust batch size and worker count
3. Use a smaller model with lower resource requirements

## Conclusion

Optimizing Files-DB-MCP performance involves balancing accuracy, resource usage, and response time. Start with the recommendations in this guide and adjust based on your specific requirements and environment constraints.

For most users, the auto-detected configuration will provide a good balance of performance and accuracy, but fine-tuning using the techniques in this guide can yield significant improvements for specific use cases.