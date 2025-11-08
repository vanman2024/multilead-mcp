#!/bin/bash
# Start Multilead MCP Server in STDIO mode (for Claude Desktop, Cursor, Claude Code)

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo -e "${GREEN}Starting Multilead MCP Server (STDIO mode)${NC}"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Warning: .env file not found${NC}"
    echo "Copy .env.example to .env and configure your API key:"
    echo "  cp .env.example .env"
    echo "  nano .env  # Edit and add your MULTILEAD_API_KEY"
    echo ""
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo -e "${RED}Error: Python is not installed${NC}"
    echo "Please install Python 3.10 or higher"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}Warning: Virtual environment not found${NC}"
    echo "Creating virtual environment..."
    python -m venv .venv
    echo "Installing dependencies..."
    source .venv/bin/activate
    pip install -e .
else
    source .venv/bin/activate
fi

# Set STDIO transport
export TRANSPORT=stdio
export LOG_LEVEL=${LOG_LEVEL:-INFO}

echo -e "${GREEN}Configuration:${NC}"
echo "  Transport: STDIO"
echo "  Log Level: $LOG_LEVEL"
echo ""
echo -e "${GREEN}Server starting...${NC}"
echo "Press Ctrl+C to stop"
echo ""

# Run server
python server.py
