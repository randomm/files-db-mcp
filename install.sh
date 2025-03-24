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
echo "NOTE: For SSH authentication, use the following command instead:"
echo "git clone git@github.com:randomm/files-db-mcp.git ~/.files-db-mcp && bash ~/.files-db-mcp/setup.sh"
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
        
        # Try cloning with SSH first (preferred for users with SSH keys)
        if ssh -T git@github.com 2>&1 | grep -q "successfully authenticated"; then
            echo "Using SSH for GitHub authentication..."
            git clone git@github.com:randomm/files-db-mcp.git "$INSTALL_DIR"
        else
            # Ask if user wants to try HTTPS instead
            echo "SSH authentication to GitHub may not be set up."
            read -p "Do you want to use HTTPS instead? (y/n) " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                git clone https://github.com/randomm/files-db-mcp.git "$INSTALL_DIR"
            else
                echo "To clone with SSH, ensure your SSH key is added to your GitHub account."
                echo "See: https://docs.github.com/en/authentication/connecting-to-github-with-ssh"
                exit 1
            fi
        fi
    fi
else
    # Option 2: Download zip file
    echo "Git not found, downloading repository as zip file..."
    
    if command -v curl >/dev/null 2>&1; then
        echo "Downloading with curl..."
        curl -L https://github.com/randomm/files-db-mcp/archive/refs/heads/main.zip -o "$INSTALL_DIR/main.zip"
        
        if command -v unzip >/dev/null 2>&1; then
            unzip -o "$INSTALL_DIR/main.zip" -d "$INSTALL_DIR-temp"
            mv "$INSTALL_DIR-temp"/*/* "$INSTALL_DIR"
            rm -rf "$INSTALL_DIR-temp" "$INSTALL_DIR/main.zip"
        else
            echo "Error: unzip command not found. Please install unzip."
            exit 1
        fi
    elif command -v wget >/dev/null 2>&1; then
        echo "Downloading with wget..."
        wget https://github.com/randomm/files-db-mcp/archive/refs/heads/main.zip -O "$INSTALL_DIR/main.zip"
        
        if command -v unzip >/dev/null 2>&1; then
            unzip -o "$INSTALL_DIR/main.zip" -d "$INSTALL_DIR-temp"
            mv "$INSTALL_DIR-temp"/*/* "$INSTALL_DIR"
            rm -rf "$INSTALL_DIR-temp" "$INSTALL_DIR/main.zip"
        else
            echo "Error: unzip command not found. Please install unzip."
            exit 1
        fi
    else
        echo "Error: Neither curl nor wget found. Please install git, curl, or wget."
        exit 1
    fi
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