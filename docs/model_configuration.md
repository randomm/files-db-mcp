# Embedding Model Configuration Guide

This document explains how to configure and use different embedding models with Files-DB-MCP.

## Supported Models

Files-DB-MCP supports a wide range of embedding models from Hugging Face, including but not limited to:

1. **General purpose models**:
   - `sentence-transformers/all-MiniLM-L6-v2` (default)
   - `sentence-transformers/all-mpnet-base-v2`
   - `BAAI/bge-small-en-v1.5`
   - `BAAI/bge-base-en-v1.5`
   - `BAAI/bge-large-en-v1.5`

2. **Code-specific models**:
   - `Salesforce/SFR-Embedding-2_R` (large but powerful)
   - `Alibaba-NLP/gte-Qwen2-1.5B-instruct` 
   - `Alibaba-NLP/gte-large-en-v1.5`
   - `nomic-ai/nomic-embed-text-v1.5`
   - `jinaai/jina-embeddings-v2-base-code`

## Model Configuration

You can configure the embedding model when starting the service:

```bash
python -m src.main --embedding-model "BAAI/bge-large-en-v1.5" --model-config '{"device": "cuda", "normalize_embeddings": true}'
```

### Configuration Options

The `--model-config` parameter accepts a JSON string with the following options:

| Option | Description | Default |
|--------|-------------|---------|
| `device` | Device to run the model on (`"cpu"`, `"cuda"`, `"mps"` for Apple Silicon) | Auto-detected |
| `normalize_embeddings` | Whether to normalize embeddings | `true` |
| `prompt_template` | Template for formatting text before embedding | `null` |
| `quantization` | Quantization type (`"int8"`, `"int4"`, `null` for no quantization) | `"int8"` if `quantization` is enabled |

## Changing Models at Runtime

You can change the embedding model at runtime through the MCP interface:

```python
import requests
import json

# Change to a code-specific model
response = requests.post(
    "http://localhost:8000/mcp",
    json={
        "function": "change_model",
        "parameters": {
            "model_name": "jinaai/jina-embeddings-v2-base-code",
            "model_config": {
                "device": "cuda",
                "normalize_embeddings": true
            }
        },
        "request_id": "123"
    }
)

print(json.dumps(response.json(), indent=2))
```

## Model Information

To get information about the currently loaded model:

```python
import requests
import json

response = requests.post(
    "http://localhost:8000/mcp",
    json={
        "function": "get_model_info",
        "request_id": "123"
    }
)

print(json.dumps(response.json(), indent=2))
```

## Recommended Models for Different Use Cases

| Use Case | Recommended Model | Notes |
|----------|------------------|-------|
| General code search | `jinaai/jina-embeddings-v2-base-code` | Good balance of performance and speed |
| High accuracy | `Salesforce/SFR-Embedding-2_R` | Very high accuracy but requires more resources |
| Small footprint | `BAAI/bge-small-en-v1.5` | Fast with lower memory usage |
| Multilingual code | `Alibaba-NLP/gte-large-en-v1.5` | Good performance for non-English code |

## Performance Considerations

1. **Memory Usage**: Larger models require more RAM or VRAM.
2. **Speed**: Smaller models are faster but may sacrifice some accuracy.
3. **Quantization**: Enables running larger models with less memory at a small accuracy cost.
4. **Device Selection**:
   - `cuda`: Fastest on NVIDIA GPUs
   - `mps`: Good for Apple Silicon Macs
   - `cpu`: Works everywhere but slower for larger models

## Advanced Configuration Example

For a production environment with a powerful GPU:

```bash
python -m src.main \
  --embedding-model "Salesforce/SFR-Embedding-2_R" \
  --model-config '{
    "device": "cuda", 
    "normalize_embeddings": true,
    "prompt_template": "Code: {text}"
  }'
```

For a development environment with limited resources:

```bash
python -m src.main \
  --embedding-model "BAAI/bge-small-en-v1.5" \
  --model-config '{
    "device": "cpu", 
    "quantization": "int8"
  }'
```