#!/usr/bin/env python3
"""
Test script for Files-DB-MCP endpoints

This script verifies that the health and MCP endpoints are working properly.
"""

import sys
import os
import json
import requests
from pathlib import Path

# Add the parent directory to the path to allow importing from src
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

def test_endpoints():
    """Test the health and MCP endpoints"""
    print("Testing Files-DB-MCP endpoints...")
    
    # Test health endpoint
    try:
        health_response = requests.get("http://localhost:3000/health", timeout=5)
        print(f"Health check status: {health_response.status_code}")
        print(f"Health check response: {health_response.json()}\n")
        
        if health_response.status_code != 200:
            print("❌ Health endpoint test failed")
            return False
        print("✓ Health endpoint test passed")
    except Exception as e:
        print(f"❌ Error connecting to health endpoint: {e}\n")
        return False

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
        
        if mcp_response.status_code != 200:
            print("❌ MCP endpoint test failed")
            return False
        print("✓ MCP endpoint test passed")
    except Exception as e:
        print(f"❌ Error connecting to MCP endpoint: {e}")
        return False
    
    print("\n✅ All endpoint tests passed")
    return True

if __name__ == "__main__":
    success = test_endpoints()
    sys.exit(0 if success else 1)