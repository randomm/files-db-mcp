# Use Case Examples

This document provides practical examples for common use cases of Files-DB-MCP.

## Table of Contents

1. [Developer Onboarding](#1-developer-onboarding)
2. [Code Review](#2-code-review)
3. [Bug Investigation](#3-bug-investigation)
4. [Feature Development](#4-feature-development)
5. [Refactoring](#5-refactoring)
6. [API Documentation](#6-api-documentation)
7. [Security Auditing](#7-security-auditing)
8. [Performance Optimization](#8-performance-optimization)
9. [Integration with Development Workflows](#9-integration-with-development-workflows)
10. [Custom MCP Client Examples](#10-custom-mcp-client-examples)

## 1. Developer Onboarding

### Use Case: New Developer Joining a Project

A new developer needs to quickly understand the codebase, find key components, and become productive.

### Examples:

#### Finding core project components:

```json
{
  "function": "search_files",
  "parameters": {
    "query": "main application entry point",
    "limit": 5
  }
}
```

#### Identifying architecture patterns:

```json
{
  "function": "search_files",
  "parameters": {
    "query": "design pattern factory singleton",
    "limit": 10
  }
}
```

#### Finding configuration files:

```json
{
  "function": "search_files",
  "parameters": {
    "query": "configuration settings",
    "file_extensions": ["json", "yaml", "xml", "conf", "ini", "toml"],
    "limit": 10
  }
}
```

#### Understanding project structure:

```bash
curl -X POST http://localhost:8000/mcp -H "Content-Type: application/json" -d '{
  "function": "search_files",
  "parameters": {
    "query": "important module core functionality",
    "limit": 20
  }
}'
```

## 2. Code Review

### Use Case: Finding Related Code During Reviews

During code reviews, developers need to find related code and understand the context of changes.

### Examples:

#### Finding code related to a Pull Request:

```json
{
  "function": "search_files",
  "parameters": {
    "query": "user authentication validation",
    "limit": 10
  }
}
```

#### Identifying similar implementations:

```json
{
  "function": "search_files",
  "parameters": {
    "query": "database connection pool management",
    "file_extensions": ["js", "ts"],
    "limit": 5
  }
}
```

#### Reviewing security implications:

```json
{
  "function": "search_files",
  "parameters": {
    "query": "input validation sanitization security",
    "limit": 10,
    "threshold": 0.75
  }
}
```

## 3. Bug Investigation

### Use Case: Tracking Down the Source of a Bug

When investigating a bug, developers need to find relevant code quickly.

### Examples:

#### Finding code related to an error message:

```bash
curl -X POST http://localhost:8000/mcp -H "Content-Type: application/json" -d '{
  "function": "search_files",
  "parameters": {
    "query": "InvalidStateError transition not allowed",
    "limit": 5,
    "threshold": 0.6
  }
}'
```

#### Locating error handling:

```json
{
  "function": "search_files",
  "parameters": {
    "query": "exception handling try catch error",
    "path_prefix": "src/services",
    "limit": 10
  }
}
```

#### Finding recent changes to a feature:

```bash
# First, find files related to the feature
curl -X POST http://localhost:8000/mcp -H "Content-Type: application/json" -d '{
  "function": "search_files",
  "parameters": {
    "query": "payment processing gateway",
    "limit": 5
  }
}'

# Then use git to examine recent changes
git log -p -- src/payments/gateway.js
```

## 4. Feature Development

### Use Case: Adding New Features

When developing new features, developers need to understand existing patterns and find relevant examples.

### Examples:

#### Finding similar features:

```json
{
  "function": "search_files",
  "parameters": {
    "query": "user notification email sms",
    "limit": 10
  }
}
```

#### Identifying extension points:

```json
{
  "function": "search_files",
  "parameters": {
    "query": "plugin extension interface",
    "limit": 5,
    "threshold": 0.7
  }
}
```

#### Understanding architectural constraints:

```json
{
  "function": "search_files",
  "parameters": {
    "query": "architectural decision record adr",
    "file_extensions": ["md"],
    "limit": 5
  }
}
```

## 5. Refactoring

### Use Case: Large-Scale Refactoring

When refactoring code, developers need to find all instances of patterns that need to be changed.

### Examples:

#### Finding deprecated patterns:

```json
{
  "function": "search_files",
  "parameters": {
    "query": "legacy api deprecated usage",
    "limit": 20,
    "threshold": 0.6
  }
}
```

#### Identifying duplication:

```json
{
  "function": "search_files",
  "parameters": {
    "query": "date parsing formatting utility",
    "limit": 15
  }
}
```

#### Finding candidates for abstraction:

```bash
curl -X POST http://localhost:8000/mcp -H "Content-Type: application/json" -d '{
  "function": "search_files",
  "parameters": {
    "query": "repeated code pattern candidate for abstraction",
    "file_extensions": ["js", "ts"],
    "limit": 20,
    "threshold": 0.65
  }
}'
```

## 6. API Documentation

### Use Case: Creating or Updating API Documentation

When working on API documentation, developers need to find all relevant endpoints and their implementations.

### Examples:

#### Finding API endpoints:

```json
{
  "function": "search_files",
  "parameters": {
    "query": "REST API endpoint route",
    "limit": 20
  }
}
```

#### Locating API validation logic:

```json
{
  "function": "search_files",
  "parameters": {
    "query": "request validation schema",
    "limit": 10,
    "path_prefix": "src/api"
  }
}
```

#### Finding authentication requirements:

```json
{
  "function": "search_files",
  "parameters": {
    "query": "API authentication authorization middleware",
    "limit": 10
  }
}
```

## 7. Security Auditing

### Use Case: Conducting a Security Review

When performing security audits, developers need to find potential vulnerabilities and security-related code.

### Examples:

#### Finding authentication mechanisms:

```json
{
  "function": "search_files",
  "parameters": {
    "query": "user authentication password hash salt",
    "limit": 10,
    "threshold": 0.7
  }
}
```

#### Identifying input validation:

```json
{
  "function": "search_files",
  "parameters": {
    "query": "input validation sanitization XSS prevention",
    "limit": 15
  }
}
```

#### Locating encryption usage:

```bash
curl -X POST http://localhost:8000/mcp -H "Content-Type: application/json" -d '{
  "function": "search_files",
  "parameters": {
    "query": "encryption cryptography sensitive data",
    "limit": 10,
    "threshold": 0.7
  }
}'
```

## 8. Performance Optimization

### Use Case: Identifying Performance Bottlenecks

When optimizing performance, developers need to find slow code, inefficient algorithms, and optimization opportunities.

### Examples:

#### Finding resource-intensive operations:

```json
{
  "function": "search_files",
  "parameters": {
    "query": "performance intensive operation slow",
    "limit": 10
  }
}
```

#### Identifying database queries:

```json
{
  "function": "search_files",
  "parameters": {
    "query": "database query join complex",
    "limit": 15,
    "threshold": 0.65
  }
}
```

#### Locating cacheable operations:

```json
{
  "function": "search_files",
  "parameters": {
    "query": "caching mechanism cache implementation",
    "limit": 10
  }
}
```

## 9. Integration with Development Workflows

### Use Case: Integrating with CI/CD Pipelines

Examples of integrating Files-DB-MCP with development workflows.

### Examples:

#### Pre-commit hook to find related tests:

```bash
#!/bin/bash
# Save as .git/hooks/pre-commit
# Make executable: chmod +x .git/hooks/pre-commit

files=$(git diff --cached --name-only --diff-filter=ACM)

for file in $files; do
  # Skip test files
  if [[ $file == *test* ]]; then
    continue
  fi
  
  # Get file content
  content=$(git show ":$file")
  
  # Extract meaningful context
  context=$(echo "$content" | grep -v "^\s*$" | grep -v "^\s*\/\/" | head -20)
  
  # Find related tests using Files-DB-MCP
  curl -s -X POST http://localhost:8000/mcp -H "Content-Type: application/json" -d '{
    "function": "search_files",
    "parameters": {
      "query": "'"$context"'",
      "file_extensions": ["test.js", "spec.js", "test.ts", "spec.ts"],
      "limit": 3
    }
  }' | jq -r '.results[].file_path' | xargs echo "Related tests for $file:"
done
```

#### GitHub Action to find code owners:

```yaml
# .github/workflows/codeowners.yml
name: Suggest Code Owners
on: [pull_request]

jobs:
  suggest-owners:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Start Files-DB-MCP
        run: docker-compose up -d
        
      - name: Find potential code owners
        run: |
          files=$(git diff --name-only ${{ github.event.pull_request.base.sha }} ${{ github.event.pull_request.head.sha }})
          for file in $files; do
            curl -s -X POST http://localhost:8000/mcp -H "Content-Type: application/json" -d '{
              "function": "search_files",
              "parameters": {
                "query": "'"$(cat $file | head -50)"'",
                "limit": 5
              }
            }' > results.json
            
            # Parse results to identify likely owners
            echo "Suggested reviewers for $file:" >> suggestion.txt
            jq -r '.results[].file_path' results.json | xargs git log --format="%an" | sort | uniq -c | sort -nr | head -3 >> suggestion.txt
          done
          
      - name: Comment on PR
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const suggestion = fs.readFileSync('suggestion.txt', 'utf8');
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: '## Suggested Code Owners\n\n' + suggestion
            });
```

## 10. Custom MCP Client Examples

### Use Case: Building Custom MCP Clients

Examples of custom clients that integrate with Files-DB-MCP.

### Examples:

#### Python MCP Client:

```python
import json
import requests

class FilesMCPClient:
    def __init__(self, url="http://localhost:8000/mcp"):
        self.url = url
        self.request_id = 0
        
    def search_files(self, query, limit=10, **kwargs):
        self.request_id += 1
        payload = {
            "function": "search_files",
            "parameters": {
                "query": query,
                "limit": limit,
                **kwargs
            },
            "request_id": f"py-{self.request_id}"
        }
        
        response = requests.post(self.url, json=payload)
        return response.json()
    
    def get_file_content(self, file_path):
        self.request_id += 1
        payload = {
            "function": "get_file_content",
            "parameters": {
                "file_path": file_path
            },
            "request_id": f"py-{self.request_id}"
        }
        
        response = requests.post(self.url, json=payload)
        return response.json()

# Usage
client = FilesMCPClient()
results = client.search_files("database connection", file_extensions=["py"])
for result in results.get("results", []):
    print(f"File: {result['file_path']}, Score: {result['score']}")
    content = client.get_file_content(result['file_path'])
    print(f"Content snippet: {content.get('content', '')[:200]}...")
```

#### JavaScript MCP Client:

```javascript
// files-mcp-client.js
class FilesMCPClient {
  constructor(url = "http://localhost:8000/mcp") {
    this.url = url;
    this.requestId = 0;
  }
  
  async searchFiles(query, limit = 10, options = {}) {
    this.requestId++;
    const payload = {
      function: "search_files",
      parameters: {
        query,
        limit,
        ...options
      },
      request_id: `js-${this.requestId}`
    };
    
    const response = await fetch(this.url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    });
    
    return await response.json();
  }
  
  async getFileContent(filePath) {
    this.requestId++;
    const payload = {
      function: "get_file_content",
      parameters: {
        file_path: filePath
      },
      request_id: `js-${this.requestId}`
    };
    
    const response = await fetch(this.url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    });
    
    return await response.json();
  }
  
  // SSE client for real-time updates
  subscribeToUpdates(callback) {
    const eventSource = new EventSource("http://localhost:8000/sse");
    
    eventSource.onmessage = (event) => {
      callback(JSON.parse(event.data));
    };
    
    eventSource.onerror = (error) => {
      console.error("SSE Error:", error);
      eventSource.close();
    };
    
    return {
      close: () => eventSource.close()
    };
  }
}

// Usage
const client = new FilesMCPClient();
async function findAuthCode() {
  const results = await client.searchFiles("authentication implementation", 5, { 
    file_extensions: ["js", "ts"] 
  });
  
  for (const result of results.results || []) {
    console.log(`File: ${result.file_path}, Score: ${result.score}`);
    const content = await client.getFileContent(result.file_path);
    console.log(`Content snippet: ${content.content?.substring(0, 200)}...`);
  }
}

// Subscribe to indexing progress
const subscription = client.subscribeToUpdates((update) => {
  if (update.type === "indexing_progress") {
    console.log(`Indexing progress: ${update.progress.toFixed(2)}%`);
  } else if (update.type === "search_result") {
    console.log(`New search result: ${update.file_path}`);
  }
});

// Close subscription when done
// subscription.close();
```

#### VS Code Extension Integration:

```typescript
// vscode-files-mcp-extension.ts
import * as vscode from 'vscode';

class FilesMCPExtension {
  private client: any;
  
  constructor() {
    // Initialize client
    this.client = {
      searchFiles: async (query: string, options = {}) => {
        // Implementation details omitted
        const response = await fetch("http://localhost:8000/mcp", {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            function: "search_files",
            parameters: { query, ...options }
          })
        });
        return await response.json();
      }
    };
  }
  
  activate(context: vscode.ExtensionContext) {
    // Register commands
    const searchCommand = vscode.commands.registerCommand('files-mcp.search', async () => {
      const query = await vscode.window.showInputBox({
        placeHolder: 'Search query',
        prompt: 'Enter a search query for Files-DB-MCP'
      });
      
      if (query) {
        const results = await this.client.searchFiles(query, 10);
        this.showResults(results);
      }
    });
    
    // Register selection-based search
    const selectionSearchCommand = vscode.commands.registerCommand('files-mcp.searchSelection', async () => {
      const editor = vscode.window.activeTextEditor;
      if (editor) {
        const selection = editor.selection;
        const text = editor.document.getText(selection);
        
        if (text) {
          const results = await this.client.searchFiles(text, 10);
          this.showResults(results);
        }
      }
    });
    
    context.subscriptions.push(searchCommand, selectionSearchCommand);
  }
  
  private showResults(results: any) {
    // Create quick pick items
    const items = results.results.map((result: any) => ({
      label: result.file_path,
      description: `Score: ${result.score.toFixed(2)}`,
      detail: result.content ? result.content.substring(0, 100) + '...' : ''
    }));
    
    // Show quick pick
    vscode.window.showQuickPick(items, {
      placeHolder: 'Select a file to open'
    }).then(item => {
      if (item) {
        vscode.workspace.openTextDocument(item.label).then(doc => {
          vscode.window.showTextDocument(doc);
        });
      }
    });
  }
}
```

These examples demonstrate various ways to integrate Files-DB-MCP into your development workflow. Adapt them to your specific needs and environment.