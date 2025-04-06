#!/bin/bash

# setup-rooflow.sh
# Script to set up RooFlow configuration files in a specified directory
# Usage: ./setup-rooflow.sh [target_directory]

set -e

# Function to display usage information
usage() {
    echo "Usage: $0 [target_directory]"
    echo "If target_directory is not specified, the current directory will be used."
    exit 1
}

# Function to display error messages
error() {
    echo "ERROR: $1" >&2
    exit 1
}

# Function to display status messages
info() {
    echo "INFO: $1"
}

# Parse command line arguments
TARGET_DIR="."
if [ $# -eq 1 ]; then
    TARGET_DIR="$1"
    # Create the directory if it doesn't exist
    mkdir -p "$TARGET_DIR" || error "Failed to create directory: $TARGET_DIR"
elif [ $# -gt 1 ]; then
    usage
fi

# Change to the target directory
cd "$TARGET_DIR" || error "Failed to change to directory: $TARGET_DIR"
info "Setting up RooFlow in $(pwd)"

# Create .roo directory if it doesn't exist
mkdir -p .roo || error "Failed to create .roo directory"
info "Created .roo directory"

# GitHub repository URL
REPO_URL="https://github.com/GreatScottyMac/RooFlow/raw/main/config"

# Files to download
FILES=(
    ".roo/system-prompt-architect"
    ".roo/system-prompt-ask"
    ".roo/system-prompt-code"
    ".roo/system-prompt-debug"
    ".roo/system-prompt-test"
    ".rooignore"
    ".roomodes"
)

# Download files from GitHub
for file in "${FILES[@]}"; do
    # Create directory structure if needed
    dir=$(dirname "$file")
    if [ "$dir" != "." ]; then
        mkdir -p "$dir" || error "Failed to create directory: $dir"
    fi
    
    # Download the file
    curl -s -L "$REPO_URL/$file" -o "$file" || error "Failed to download $file"
    info "Downloaded $file"
done

# Download the appropriate insert-variables script based on OS
if [[ "$OSTYPE" == "darwin"* ]] || [[ "$OSTYPE" == "linux"* ]]; then
    # macOS or Linux
    curl -s -L "$REPO_URL/insert-variables.sh" -o "insert-variables.sh" || error "Failed to download insert-variables.sh"
    chmod +x insert-variables.sh || error "Failed to make insert-variables.sh executable"
    info "Downloaded insert-variables.sh"
elif [[ "$OSTYPE" == "msys"* ]] || [[ "$OSTYPE" == "win"* ]]; then
    # Windows
    curl -s -L "$REPO_URL/insert-variables.cmd" -o "insert-variables.cmd" || error "Failed to download insert-variables.cmd"
    info "Downloaded insert-variables.cmd"
else
    error "Unsupported operating system: $OSTYPE"
fi

# Run the insert-variables script
info "Running insert-variables script to replace placeholders..."
if [[ "$OSTYPE" == "darwin"* ]] || [[ "$OSTYPE" == "linux"* ]]; then
    # macOS or Linux
    ./insert-variables.sh || error "Failed to run insert-variables.sh"
elif [[ "$OSTYPE" == "msys"* ]] || [[ "$OSTYPE" == "win"* ]]; then
    # Windows
    cmd /c insert-variables.cmd || error "Failed to run insert-variables.cmd"
fi

info "RooFlow setup completed successfully!"
info "Your project structure now includes:"
info "- .roo/ directory with system prompt files"
info "- .rooignore and .roomodes configuration files"
info "- The Memory Bank will be created automatically when you first use Roo"

echo ""
echo "Next steps:"
echo "1. Open your project in VS Code with the Roo Code extension installed"
echo "2. Start using Roo with the enhanced Memory Bank functionality"