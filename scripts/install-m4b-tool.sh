#!/bin/bash
# Install m4b-tool Docker wrapper for ReadarrM4B

set -e

echo "Setting up m4b-tool Docker wrapper..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed. Please install Docker first."
    exit 1
fi

# Pull the m4b-tool Docker image
echo "Pulling m4b-tool Docker image..."
docker pull sandreas/m4b-tool:latest

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Copy wrapper to system path
echo "Installing m4b-tool wrapper..."
sudo cp "$SCRIPT_DIR/m4b-tool-wrapper" /usr/local/bin/m4b-tool
sudo chmod +x /usr/local/bin/m4b-tool

# Test the installation
echo "Testing m4b-tool installation..."
if m4b-tool --version &> /dev/null; then
    echo "✅ m4b-tool successfully installed!"
    echo "You can now run: python src/main.py --convert /path/to/audiobook"
else
    echo "❌ m4b-tool installation failed"
    exit 1
fi