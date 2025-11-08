#!/bin/bash
#
# Start Multilead MCP Server in STDIO mode (for Claude Desktop/Code)
#
# This script starts the server with STDIO transport for local IDE integration.
# Make sure your .env file is configured with MULTILEAD_API_KEY.
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Error: .env file not found. Copy .env.example to .env and configure it."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d .venv ]; then
    echo "Error: Virtual environment not found. Run: uv venv or python -m venv .venv"
    exit 1
fi

# Activate virtual environment
source .venv/bin/activate

# Set STDIO transport explicitly
export TRANSPORT=stdio

echo "Starting Multilead MCP Server in STDIO mode..."
echo "Press Ctrl+C to stop"
echo ""

# Run server
python server.py
