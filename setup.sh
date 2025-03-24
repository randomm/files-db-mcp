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

# Create alias in ~/.bashrc or ~/.zshrc
SHELL_RC=""
if [ -f "$HOME/.zshrc" ]; then
    SHELL_RC="$HOME/.zshrc"
elif [ -f "$HOME/.bashrc" ]; then
    SHELL_RC="$HOME/.bashrc"
fi

if [ -n "$SHELL_RC" ]; then
    echo "Adding alias to $SHELL_RC..."
    
    # Remove old alias if it exists
    sed -i.bak '/alias files-db-mcp=/d' "$SHELL_RC"
    
    # Add new alias
    echo "alias files-db-mcp='$SCRIPT_DIR/run.sh'" >> "$SHELL_RC"
    
    echo "Alias added. You can now use 'files-db-mcp' command in any project directory."
    echo "Please restart your shell or run 'source $SHELL_RC' to use the command."
else
    echo "Could not find .zshrc or .bashrc to add alias."
    echo "To use Files-DB-MCP, run:"
    echo "  $SCRIPT_DIR/run.sh"
fi

# Make scripts executable
chmod +x "$SCRIPT_DIR/run.sh"

echo
echo "Setup complete!"
echo
echo "To start Files-DB-MCP in any project directory, simply run:"
echo "  files-db-mcp"
echo
echo "Happy coding!"