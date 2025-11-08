# Multilead MCP Server - Quick Start

Fast deployment instructions for both STDIO and HTTP modes.

## Prerequisites

- Python 3.10 or higher
- Multilead API key from https://app.multilead.co/settings/api

## STDIO Mode (Claude Desktop/Code)

### 1. Install & Configure

```bash
cd /home/gotime2022/Projects/mcp-servers/multilead-mcp

# Install dependencies
uv venv && source .venv/bin/activate
uv pip install -e .

# Configure
cp .env.example .env
# Edit .env and set MULTILEAD_API_KEY
```

### 2. Test Locally

```bash
python server.py
# Press Ctrl+C to stop
```

### 3. Configure Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "multilead": {
      "command": "python",
      "args": ["/home/gotime2022/Projects/mcp-servers/multilead-mcp/server.py"],
      "env": {
        "MULTILEAD_API_KEY": "your_multilead_api_key_here"
      }
    }
  }
}
```

**Config file location:**
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

### 4. Restart Claude Desktop

Done! The Multilead server is now available in Claude Desktop.

---

## HTTP Mode (Web Services)

### 1. Install & Configure

```bash
cd /home/gotime2022/Projects/mcp-servers/multilead-mcp

# Install dependencies
uv venv && source .venv/bin/activate
uv pip install -e .

# Configure for HTTP
cp .env.example .env
# Edit .env:
#   MULTILEAD_API_KEY=your_key_here
#   TRANSPORT=http
#   HOST=0.0.0.0
#   PORT=8000
```

### 2. Start HTTP Server

```bash
# Option 1: Using script
./scripts/start-http.sh

# Option 2: Direct
TRANSPORT=http python server.py

# Option 3: Custom port
TRANSPORT=http PORT=3000 python server.py
```

### 3. Test Server

```bash
# Health check
curl http://localhost:8000/health

# Expected: {"status": "healthy", ...}
```

### 4. Connect Claude Desktop (HTTP)

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "multilead": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

Done! The Multilead server is now accessible via HTTP.

---

## Quick Commands

```bash
# STDIO mode
python server.py

# HTTP mode (default port 8000)
TRANSPORT=http python server.py

# HTTP mode (custom port)
TRANSPORT=http PORT=3000 python server.py

# HTTP mode (localhost only)
TRANSPORT=http HOST=127.0.0.1 python server.py

# Debug mode
LOG_LEVEL=DEBUG MULTILEAD_DEBUG=true python server.py

# Using startup scripts
./scripts/start-stdio.sh
./scripts/start-http.sh
```

---

## Endpoints (HTTP Mode)

- **MCP Endpoint**: `http://localhost:8000/mcp`
- **Health Check**: `http://localhost:8000/health`

---

## Troubleshooting

**Server won't start:**
```bash
# Check Python version
python --version  # Must be 3.10+

# Reinstall dependencies
pip install -e .
```

**Authentication errors:**
```bash
# Verify API key is set
cat .env | grep MULTILEAD_API_KEY

# Test API key
curl -H "Authorization: Bearer your_key" https://api.multilead.co/v1/leads
```

**Port already in use:**
```bash
# Use different port
PORT=3001 TRANSPORT=http python server.py
```

**Cannot connect remotely:**
```bash
# Bind to all interfaces
HOST=0.0.0.0 TRANSPORT=http python server.py

# Open firewall
sudo ufw allow 8000/tcp
```

---

## Next Steps

- Full deployment guide: `docs/deployment/DEPLOYMENT_GUIDE.md`
- Environment variables: See `.env.example`
- Production deployment: See systemd/Docker examples in deployment guide
- API documentation: https://docs.multilead.co/api-reference

## Support

- Server issues: Open issue in repository
- Multilead API: https://app.multilead.co/support
- FastMCP: https://gofastmcp.com
