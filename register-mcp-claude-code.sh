#!/bin/bash

# Registration script for Claude Code CLI using Docker
# This makes the Databricks MCP server available across all Claude Code projects

set -e  # Exit on error

echo "🐳 Registering Databricks MCP server with Claude Code CLI (Docker)..."

# Get the current working directory for proper paths
CURRENT_DIR=$(pwd)

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker is not installed"
    echo "Please install Docker first: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if databricks_connections.json exists
if [ ! -f "$CURRENT_DIR/databricks_connections.json" ]; then
    echo "⚠️  Warning: databricks_connections.json not found"
    echo "Please create it before using the MCP server"
    echo "See databricks_connections_example.json for reference"
fi

# Build the Docker image
echo "🔨 Building Docker image..."
docker build -t databricks-mcp:latest "$CURRENT_DIR"

if [ $? -ne 0 ]; then
    echo "❌ Failed to build Docker image"
    exit 1
fi

echo "✅ Docker image built successfully"
echo ""

# Remove existing server from user scope
echo "🔧 Removing existing server from user scope (if any)..."
claude mcp remove -s user databricks 2>/dev/null || true

# Register the server using docker run command
echo "📝 Registering server at user scope..."

# The docker run command that will be used by Claude Code
# Note: We mount the databricks_connections.json from the project directory
claude mcp add -s user databricks \
    docker run --rm -i \
    -v "$CURRENT_DIR/databricks_connections.json:/app/databricks_connections.json:ro" \
    databricks-mcp:latest

if [ $? -eq 0 ]; then
    echo "✅ Successfully registered databricks MCP server globally"
    echo ""
    echo "📋 Configuration:"
    echo "   - Image: databricks-mcp:latest"
    echo "   - Config: $CURRENT_DIR/databricks_connections.json"
    echo "   - Scope: user (global)"
    echo ""
    echo "✨ The server is now available across all your Claude Code projects!"
    echo ""
    echo "Run 'claude mcp list' to verify the configuration."
else
    echo "❌ Failed to register server"
    exit 1
fi
