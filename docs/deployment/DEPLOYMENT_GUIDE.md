# Multilead MCP Server Deployment Guide

Complete guide for deploying the Multilead MCP Server in different environments with both STDIO and HTTP transports.

## Table of Contents

1. [Overview](#overview)
2. [Transport Modes](#transport-modes)
3. [STDIO Deployment (Claude Desktop/Code)](#stdio-deployment)
4. [HTTP Deployment (Web Services)](#http-deployment)
5. [Environment Variables](#environment-variables)
6. [Production Features](#production-features)
7. [Monitoring](#monitoring)
8. [Troubleshooting](#troubleshooting)

---

## Overview

The Multilead MCP Server supports two transport modes:

- **STDIO** - Standard Input/Output for local IDE integration (Claude Desktop, Claude Code, Cursor)
- **HTTP** - Network-accessible HTTP server for remote clients and web services

The transport mode is selected via the `TRANSPORT` environment variable, making it easy to switch between modes without code changes.

---

## Transport Modes

### STDIO Transport (Default)

**Use Cases:**
- Claude Desktop integration
- Claude Code integration
- Cursor integration
- Local development and testing
- Single-user scenarios

**Benefits:**
- Simple configuration
- No network setup required
- Runs locally with full system access
- Direct process communication

**Limitations:**
- Single client only
- No remote access
- Requires local installation

### HTTP Transport

**Use Cases:**
- Team deployments
- Remote access
- Web service integration
- Multi-client scenarios
- Production environments
- Container deployments

**Benefits:**
- Multiple concurrent clients
- Remote accessibility
- Standard web protocols
- Load balancer compatible
- Health check endpoints

**Limitations:**
- Requires network configuration
- Security considerations (CORS, authentication)
- More complex setup

---

## STDIO Deployment

### Quick Start

1. **Install Dependencies**

```bash
cd /home/gotime2022/Projects/mcp-servers/multilead-mcp

# Using uv (recommended)
uv venv
source .venv/bin/activate
uv pip install -e .

# Or using pip
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

2. **Configure Environment**

```bash
cp .env.example .env
```

Edit `.env` and set your API key:

```env
MULTILEAD_API_KEY=your_multilead_api_key_here
TRANSPORT=stdio
```

3. **Start Server**

```bash
# Option 1: Direct Python
python server.py

# Option 2: Use startup script
./scripts/start-stdio.sh

# Option 3: Using FastMCP CLI
fastmcp run server.py
```

### Claude Desktop Integration

**Configuration File Location:**
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

**Configuration (STDIO):**

```json
{
  "mcpServers": {
    "multilead": {
      "command": "python",
      "args": [
        "/home/gotime2022/Projects/mcp-servers/multilead-mcp/server.py"
      ],
      "env": {
        "MULTILEAD_API_KEY": "your_multilead_api_key_here",
        "TRANSPORT": "stdio"
      }
    }
  }
}
```

**Using Virtual Environment:**

```json
{
  "mcpServers": {
    "multilead": {
      "command": "/home/gotime2022/Projects/mcp-servers/multilead-mcp/.venv/bin/python",
      "args": [
        "/home/gotime2022/Projects/mcp-servers/multilead-mcp/server.py"
      ],
      "env": {
        "MULTILEAD_API_KEY": "your_multilead_api_key_here"
      }
    }
  }
}
```

**Using uv:**

```json
{
  "mcpServers": {
    "multilead": {
      "command": "uv",
      "args": [
        "run",
        "--with", "fastmcp>=2.13.0",
        "--with", "httpx>=0.27.0",
        "--with", "pydantic>=2.0.0",
        "--with", "python-dotenv>=1.0.0",
        "fastmcp",
        "run",
        "/home/gotime2022/Projects/mcp-servers/multilead-mcp/server.py"
      ],
      "env": {
        "MULTILEAD_API_KEY": "your_multilead_api_key_here"
      }
    }
  }
}
```

### Claude Code Integration

**Installation:**

```bash
# Option 1: Using FastMCP CLI (recommended)
fastmcp install claude-code server.py \
  --server-name "Multilead" \
  --env MULTILEAD_API_KEY=your_key_here

# Option 2: Manual installation
claude mcp add multilead -- python /home/gotime2022/Projects/mcp-servers/multilead-mcp/server.py
```

**Manual Configuration (`.claude/mcp.json`):**

```json
{
  "mcpServers": {
    "multilead": {
      "command": "python",
      "args": [
        "/home/gotime2022/Projects/mcp-servers/multilead-mcp/server.py"
      ],
      "env": {
        "MULTILEAD_API_KEY": "your_multilead_api_key_here"
      }
    }
  }
}
```

---

## HTTP Deployment

### Quick Start

1. **Configure Environment**

```bash
cp .env.example .env
```

Edit `.env`:

```env
MULTILEAD_API_KEY=your_multilead_api_key_here
TRANSPORT=http
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO
```

2. **Start HTTP Server**

```bash
# Option 1: Using startup script
./scripts/start-http.sh

# Option 2: Direct Python with environment variables
TRANSPORT=http python server.py

# Option 3: Custom port
TRANSPORT=http PORT=3000 python server.py

# Option 4: Localhost only
TRANSPORT=http HOST=127.0.0.1 python server.py
```

### Available Endpoints

Once running, the server exposes:

- **MCP Endpoint**: `http://localhost:8000/mcp` - Main MCP JSON-RPC endpoint
- **Health Check**: `http://localhost:8000/health` - Health monitoring endpoint

### Testing HTTP Server

```bash
# Test health endpoint
curl http://localhost:8000/health

# Expected response:
# {
#   "status": "healthy",
#   "service": "multilead-mcp",
#   "version": "1.0.0",
#   "timestamp": "2025-01-15T10:30:00Z",
#   "transport": "http",
#   "api_configured": true
# }
```

### Claude Desktop Integration (HTTP)

```json
{
  "mcpServers": {
    "multilead": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

### Production Deployment

#### Using systemd (Linux)

Create `/etc/systemd/system/multilead-mcp.service`:

```ini
[Unit]
Description=Multilead MCP Server
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/home/gotime2022/Projects/mcp-servers/multilead-mcp
Environment="TRANSPORT=http"
Environment="HOST=0.0.0.0"
Environment="PORT=8000"
Environment="LOG_LEVEL=WARNING"
Environment="MULTILEAD_API_KEY=your_key_here"
ExecStart=/home/gotime2022/Projects/mcp-servers/multilead-mcp/.venv/bin/python server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Manage service:**

```bash
# Start service
sudo systemctl start multilead-mcp

# Enable on boot
sudo systemctl enable multilead-mcp

# View logs
sudo journalctl -u multilead-mcp -f

# Restart service
sudo systemctl restart multilead-mcp
```

#### Using Docker

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY pyproject.toml .
RUN pip install -e .

# Copy server code
COPY server.py .

# Environment variables (override at runtime)
ENV TRANSPORT=http
ENV HOST=0.0.0.0
ENV PORT=8000
ENV LOG_LEVEL=INFO

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# Expose port
EXPOSE 8000

# Run server
CMD ["python", "server.py"]
```

**Build and run:**

```bash
# Build image
docker build -t multilead-mcp .

# Run container
docker run -d \
  --name multilead-mcp \
  -p 8000:8000 \
  -e MULTILEAD_API_KEY=your_key_here \
  -e TRANSPORT=http \
  multilead-mcp

# View logs
docker logs -f multilead-mcp

# Health check
curl http://localhost:8000/health
```

#### Using Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  multilead-mcp:
    build: .
    container_name: multilead-mcp
    ports:
      - "8000:8000"
    environment:
      - MULTILEAD_API_KEY=${MULTILEAD_API_KEY}
      - TRANSPORT=http
      - HOST=0.0.0.0
      - PORT=8000
      - LOG_LEVEL=INFO
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 3s
      retries: 3
      start_period: 5s
```

**Run:**

```bash
# Start service
docker-compose up -d

# View logs
docker-compose logs -f

# Stop service
docker-compose down
```

---

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `MULTILEAD_API_KEY` | Your Multilead API key | `ml_live_abc123...` |

### Optional API Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MULTILEAD_BASE_URL` | `https://api.multilead.co` | Multilead API base URL |
| `MULTILEAD_TIMEOUT` | `30` | Request timeout (seconds) |
| `MULTILEAD_DEBUG` | `false` | Enable debug logging |

### Optional Transport Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `TRANSPORT` | `stdio` | Transport mode: `stdio` or `http` |
| `HOST` | `0.0.0.0` | HTTP server host (HTTP mode only) |
| `PORT` | `8000` | HTTP server port (HTTP mode only) |
| `LOG_LEVEL` | `INFO` | Logging level: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` |

### Environment Configuration Files

**Development (`.env`):**
```env
MULTILEAD_API_KEY=your_dev_key_here
TRANSPORT=stdio
LOG_LEVEL=DEBUG
MULTILEAD_DEBUG=true
```

**Production (`.env.production`):**
```env
MULTILEAD_API_KEY=your_prod_key_here
TRANSPORT=http
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=WARNING
MULTILEAD_DEBUG=false
MULTILEAD_TIMEOUT=60
```

---

## Production Features

### Health Check Endpoint

**Endpoint:** `GET /health`

**Response (Healthy):**
```json
{
  "status": "healthy",
  "service": "multilead-mcp",
  "version": "1.0.0",
  "timestamp": "2025-01-15T10:30:00Z",
  "transport": "http",
  "api_configured": true
}
```

**Response (Unhealthy):**
```json
{
  "status": "unhealthy",
  "service": "multilead-mcp",
  "version": "1.0.0",
  "timestamp": "2025-01-15T10:30:00Z",
  "transport": "http",
  "api_configured": false,
  "error": "MULTILEAD_API_KEY environment variable is required"
}
```

**Status Codes:**
- `200 OK` - Server healthy
- `503 Service Unavailable` - Server unhealthy

### Logging

The server uses structured logging with configurable levels:

```bash
# Development: Verbose logging
LOG_LEVEL=DEBUG python server.py

# Production: Minimal logging
LOG_LEVEL=WARNING python server.py

# Critical errors only
LOG_LEVEL=ERROR python server.py
```

### Error Handling

The server includes comprehensive error handling:

- **Authentication errors** - Clear messages for invalid API keys
- **Network errors** - Detailed connection issue reporting
- **Rate limiting** - Automatic retry with backoff
- **Timeout errors** - Configurable timeout handling
- **Validation errors** - Helpful input validation messages

---

## Monitoring

### Health Check Integration

**Uptime monitoring services:**

```bash
# UptimeRobot, Pingdom, etc.
https://your-server.com/health
```

**Load balancer health checks:**

```nginx
# nginx upstream configuration
upstream multilead_mcp {
    server localhost:8000 max_fails=3 fail_timeout=30s;
}

# Health check
location /health {
    proxy_pass http://multilead_mcp/health;
}
```

### Log Monitoring

**View logs in real-time:**

```bash
# Systemd
sudo journalctl -u multilead-mcp -f

# Docker
docker logs -f multilead-mcp

# Docker Compose
docker-compose logs -f multilead-mcp

# Direct run
TRANSPORT=http LOG_LEVEL=INFO python server.py 2>&1 | tee server.log
```

### Metrics

Monitor these key metrics:

- **Health endpoint uptime** - Should always return 200 OK
- **Response time** - Health endpoint latency
- **Error rate** - Failed requests to Multilead API
- **Memory usage** - Python process memory
- **CPU usage** - Server load

---

## Troubleshooting

### STDIO Mode Issues

**Issue: Server not starting**

```bash
# Check Python version
python --version  # Should be 3.10+

# Check dependencies
pip list | grep fastmcp

# Reinstall dependencies
pip install -e .
```

**Issue: Claude Desktop not connecting**

1. Check configuration file path is correct
2. Verify API key is set in `env` section
3. Use absolute paths, not relative paths
4. Restart Claude Desktop after config changes

### HTTP Mode Issues

**Issue: Port already in use**

```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
PORT=3000 TRANSPORT=http python server.py
```

**Issue: Cannot connect remotely**

```bash
# Check firewall
sudo ufw status
sudo ufw allow 8000/tcp

# Verify binding to all interfaces
HOST=0.0.0.0 TRANSPORT=http python server.py

# Test connectivity
curl http://localhost:8000/health
curl http://your-server-ip:8000/health
```

### API Issues

**Issue: Authentication failed**

```bash
# Verify API key is set
echo $MULTILEAD_API_KEY

# Test API key directly
curl -H "Authorization: Bearer your_key_here" \
  https://api.multilead.co/v1/leads
```

**Issue: Rate limiting**

- Wait a few minutes before retrying
- Increase timeout: `MULTILEAD_TIMEOUT=60`
- Check Multilead API limits at dashboard

**Issue: Timeout errors**

```bash
# Increase timeout
export MULTILEAD_TIMEOUT=60

# Check network connectivity
ping api.multilead.co

# Test API directly
curl -w "@curl-format.txt" https://api.multilead.co/v1/leads
```

### Debug Mode

Enable debug logging for detailed troubleshooting:

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
export MULTILEAD_DEBUG=true

# Run server
python server.py
```

---

## Next Steps

- **Testing**: See `docs/testing/TESTING_GUIDE.md` for testing procedures
- **Development**: See `docs/development/DEVELOPMENT_GUIDE.md` for adding features
- **API Reference**: See Multilead API docs at https://docs.multilead.co/api-reference

## Support

- **Server Issues**: Open issue in repository
- **Multilead API**: https://app.multilead.co/support
- **FastMCP Framework**: https://gofastmcp.com
