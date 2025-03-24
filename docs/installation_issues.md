# Installation Issues Tracker

## TASK-021: Fix installation script paths [RESOLVED]

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

### Fix Implemented
1. Added a fallback mechanism in `scripts/run.sh` to check for docker-compose.yml in the base directory and the `.files-db-mcp` directory
2. Modified the installation script to copy docker-compose.yml to the scripts directory
3. Updated troubleshooting documentation with a manual fix for existing installations

### Verification
The fix has been tested with a fresh installation and works correctly. Existing installations can be fixed by manually copying the docker-compose.yml file to the scripts directory:
```bash
cp ~/.files-db-mcp/docker-compose.yml ~/.files-db-mcp/scripts/
```

### Status
RESOLVED

### Resolved by
Claude

### Resolution Date
March 24, 2025