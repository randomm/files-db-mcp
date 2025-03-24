#!/bin/bash
# Installation script for Files-DB-MCP

# Stop on error
set -e

# Print banner
echo "=================================================="
echo "  Files-DB-MCP - Vector Search for Code Projects  "
echo "=================================================="
echo "             Installation Script                   "
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

# Determine installation directory
INSTALL_DIR="$HOME/.files-db-mcp"
mkdir -p "$INSTALL_DIR"

# Clone repository or download files
echo "Installing Files-DB-MCP to $INSTALL_DIR..."

# Option 1: Clone from git repository
if command -v git >/dev/null 2>&1; then
    if [ -d "$INSTALL_DIR/.git" ]; then
        echo "Updating existing installation..."
        cd "$INSTALL_DIR"
        git pull
    else
        echo "Cloning repository..."
        git clone https://github.com/randomm/files-db-mcp.git "$INSTALL_DIR"
    fi
else
    # Option 2: Download zip file (placeholder)
    echo "Git not found, downloading files directly..."
    # This would be implemented with curl or wget to download a zip file
    echo "Not implemented yet, please install git"
    exit 1
fi

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
    echo "alias files-db-mcp='$INSTALL_DIR/run.sh'" >> "$SHELL_RC"
    
    echo "Alias added. You can now use 'files-db-mcp' command in any project directory."
    echo "Please restart your shell or run 'source $SHELL_RC' to use the command."
else
    echo "Could not find .zshrc or .bashrc to add alias."
    echo "To use Files-DB-MCP, run:"
    echo "  $INSTALL_DIR/run.sh"
fi

# Make scripts executable
chmod +x "$INSTALL_DIR/run.sh"

echo
echo "Installation complete!"
echo
echo "To start Files-DB-MCP in any project directory, simply run:"
echo "  files-db-mcp"
echo
echo "Happy coding!"