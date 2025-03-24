# Installation Issues Tracker

## TASK-021: Fix installation script paths

### Description
The installation process is failing when users try to run the `files-db-mcp` command. The script is unable to find the docker-compose.yml file at the expected location.

Error message:
```
nornene on 🌱refactoring-system [$⇡]
❯ files-db-mcp
==================================================
  Files-DB-MCP - Vector Search for Code Projects
==================================================

Starting Files-DB-MCP for project: /Users/janni/git/nornene

Cleaning up any existing containers...
open /Users/janni/.files-db-mcp/scripts/docker-compose.yml: no such file or directory
```

### Steps to Reproduce
1. Follow the installation instructions from README.md
2. Run the `files-db-mcp` command in any directory

### Expected Behavior
The command should start the files-db-mcp service without errors.

### Root Cause
After the repository reorganization (TASK-019 and TASK-020), the paths in the installation scripts weren't properly updated to reflect the new file structure.

### Priority
High - This affects all new users trying to use the tool.

### Assigned to
Claude

### Due Date
ASAP