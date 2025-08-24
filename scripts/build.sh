#!/bin/bash

# Build script for MCP Speech-to-Text Docker image
# Cross-platform support for Linux, macOS, and Windows (via Git Bash/WSL)

set -e

# Detect OS
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then
    IS_WINDOWS=true
    echo "Detected Windows environment"
else
    IS_WINDOWS=false
fi

echo "Building MCP Speech-to-Text Docker image..."

# Get version from pyproject.toml
if command -v grep &> /dev/null && command -v cut &> /dev/null; then
    VERSION=$(grep '^version = ' pyproject.toml | cut -d '"' -f 2)
else
    # Fallback for Windows without grep/cut
    VERSION="1.0.0"
    echo "Warning: Could not parse version from pyproject.toml, using default: $VERSION"
fi

# Check if Docker is installed and running
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker is not installed or not in PATH"
    echo "Please install Docker Desktop from: https://www.docker.com/products/docker-desktop"
    exit 1
fi

# Check if Docker daemon is running
if ! docker info &> /dev/null; then
    echo "❌ Error: Docker daemon is not running"
    if [[ "$IS_WINDOWS" == true ]]; then
        echo "Please start Docker Desktop"
    else
        echo "Please start Docker service"
    fi
    exit 1
fi

# Build the Docker image
echo "📦 Building Docker image: mcp-speech-to-text:${VERSION}"
docker build -t mcp-speech-to-text:${VERSION} .

if [ $? -eq 0 ]; then
    echo "✅ Build successful"
    docker tag mcp-speech-to-text:${VERSION} mcp-speech-to-text:latest
    echo "🏷️  Tagged as latest"
else
    echo "❌ Build failed"
    exit 1
fi

echo "Docker image built successfully:"
echo "  - mcp-speech-to-text:${VERSION}"
echo "  - mcp-speech-to-text:latest"

# Display image size
IMAGE_SIZE=$(docker images mcp-speech-to-text:${VERSION} --format "{{.Size}}")
echo "📊 Image size: ${IMAGE_SIZE}"

# Optional: Push to registry (uncomment if needed)
# echo "Pushing to registry..."
# docker push mcp-speech-to-text:${VERSION}
# docker push mcp-speech-to-text:latest

echo ""
echo "🎉 Build completed!"
echo ""
echo "To run the container:"
if [[ "$IS_WINDOWS" == true ]]; then
    echo "  docker run -p 8000:8000 mcp-speech-to-text:${VERSION}"
else
    echo "  ./start.sh"
    echo "  # or"
    echo "  docker run -p 8000:8000 mcp-speech-to-text:${VERSION}"
fi
echo ""
echo "To run with Docker Compose:"
echo "  docker-compose up -d"
