#!/bin/bash
# Start Multilead MCP Server in HTTP mode (for web services, remote access)

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo -e "${GREEN}Starting Multilead MCP Server (HTTP mode)${NC}"

# Parse command line arguments
HOST=${HOST:-0.0.0.0}
PORT=${PORT:-8000}
LOG_LEVEL=${LOG_LEVEL:-INFO}
LOG_FORMAT=${LOG_FORMAT:-text}

while [[ $# -gt 0 ]]; do
    case $1 in
        --host)
            HOST="$2"
            shift 2
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        --log-level)
            LOG_LEVEL="$2"
            shift 2
            ;;
        --log-format)
            LOG_FORMAT="$2"
            shift 2
            ;;
        --production)
            LOG_FORMAT="json"
            shift
            ;;
        --help)
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --host HOST          Bind to HOST (default: 0.0.0.0)"
            echo "  --port PORT          Bind to PORT (default: 8000)"
            echo "  --log-level LEVEL    Set log level: DEBUG, INFO, WARNING, ERROR, CRITICAL (default: INFO)"
            echo "  --log-format FORMAT  Set log format: text or json (default: text)"
            echo "  --production         Enable production mode (JSON logs, stricter settings)"
            echo "  --help               Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                                    # Start on 0.0.0.0:8000"
            echo "  $0 --host 127.0.0.1 --port 3000       # Start on localhost:3000"
            echo "  $0 --production                       # Start in production mode"
            exit 0
            ;;
        *)
            echo -e "${RED}Error: Unknown option $1${NC}"
            echo "Run '$0 --help' for usage information"
            exit 1
            ;;
    esac
done

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

# Set HTTP transport
export TRANSPORT=http
export HOST=$HOST
export PORT=$PORT
export LOG_LEVEL=$LOG_LEVEL
export LOG_FORMAT=$LOG_FORMAT

# Create logs directory
mkdir -p logs

echo ""
echo -e "${GREEN}Configuration:${NC}"
echo "  Transport: HTTP"
echo "  Host: $HOST"
echo "  Port: $PORT"
echo "  Log Level: $LOG_LEVEL"
echo "  Log Format: $LOG_FORMAT"
echo ""
echo -e "${BLUE}Server Endpoints:${NC}"
if [ "$HOST" = "0.0.0.0" ]; then
    echo "  MCP Endpoint: http://localhost:$PORT/mcp"
    echo "  Health Check: http://localhost:$PORT/health"
else
    echo "  MCP Endpoint: http://$HOST:$PORT/mcp"
    echo "  Health Check: http://$HOST:$PORT/health"
fi
echo ""
echo -e "${GREEN}Server starting...${NC}"
echo "Press Ctrl+C to stop"
echo ""

# Run server
python server.py
