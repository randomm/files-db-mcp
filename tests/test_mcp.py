import requests
import json
import sys

# Test health endpoint
try:
    health_response = requests.get("http://localhost:3000/health", timeout=5)
    print(f"Health check status: {health_response.status_code}")
    print(f"Health check response: {health_response.json()}\n")
except Exception as e:
    print(f"Error connecting to health endpoint: {e}\n")

# Test MCP endpoint with a simple search query
try:
    mcp_request = {
        "function": "search_files",
        "parameters": {
            "query": "vector database",
            "limit": 5
        },
        "request_id": "test_request_123"
    }
    
    mcp_response = requests.post(
        "http://localhost:3000/mcp", 
        json=mcp_request,
        timeout=5
    )
    
    print(f"MCP endpoint status: {mcp_response.status_code}")
    print(f"MCP response: {json.dumps(mcp_response.json(), indent=2)}")
except Exception as e:
    print(f"Error connecting to MCP endpoint: {e}")
