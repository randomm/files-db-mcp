#!/bin/bash
# Setup script for Files-DB-MCP (called after cloning)

# Stop on error
set -e

# Print banner
echo "=================================================="
echo "  Files-DB-MCP - Vector Search for Code Projects  "
echo "=================================================="
echo "               Setup Script                       "
echo "=================================================="
echo

# Check if Docker and Docker Compose are installed
if ! command -v docker >/dev/null 2>&1; then
    echo "Warning: Docker is not installed or not in PATH"
    echo "Please install Docker: https://docs.docker.com/get-docker/"
    echo
    read -p "Do you want to continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

if ! docker compose version >/dev/null 2>&1; then
    echo "Warning: Docker Compose is not installed or not in PATH"
    echo "Please install Docker Compose: https://docs.docker.com/compose/install/"
    echo
    read -p "Do you want to continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Determine installation directory - use directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
INSTALL_DIR="$HOME/.files-db-mcp"

# Suggest how to add alias
echo "To add a convenient alias for Files-DB-MCP, add the following line to your shell profile:"
echo
echo "  alias files-db-mcp='$SCRIPT_DIR/run.sh'"
echo
echo "For example, in ~/.bashrc, ~/.zshrc, or your preferred shell configuration file."
echo "After adding the alias, run 'source ~/.bashrc' (or your shell config file) to activate it."
echo
echo "Alternatively, you can run Files-DB-MCP directly with:"
echo "  $SCRIPT_DIR/run.sh"
echo

# Make scripts executable
chmod +x "$SCRIPT_DIR/run.sh"

echo
echo "Setup complete!"
echo
echo "To start Files-DB-MCP in any project directory, simply run:"
echo "  files-db-mcp"
echo
echo "Happy coding!"