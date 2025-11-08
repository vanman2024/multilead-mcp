# Multilead MCP Server Deployment Guide

Complete guide for deploying the Multilead MCP Server in different environments.

## Table of Contents

- [Quick Start](#quick-start)
- [Deployment Options](#deployment-options)
- [STDIO Deployment (Local/IDE)](#stdio-deployment-localide)
- [HTTP Deployment (Remote Access)](#http-deployment-remote-access)
- [Production Configuration](#production-configuration)
- [Monitoring and Logging](#monitoring-and-logging)
- [Troubleshooting](#troubleshooting)

## Quick Start

### For Claude Desktop/Code (STDIO)

```bash
# 1. Configure environment
cp .env.example .env
nano .env  # Add your MULTILEAD_API_KEY

# 2. Start server
./start.sh
```

### For Remote Access (HTTP)

```bash
# 1. Configure environment
cp .env.example .env
nano .env  # Add your MULTILEAD_API_KEY

# 2. Start HTTP server
./start-http.sh --host 0.0.0.0 --port 8000
```

## Deployment Options

The Multilead MCP Server supports multiple deployment configurations:

| Transport | Use Case | Configuration |
|-----------|----------|---------------|
| **STDIO** | Claude Desktop, Cursor, Claude Code | Local process, JSON-RPC over stdin/stdout |
| **HTTP** | Remote access, web services, cloud deployment | HTTP server with REST API |

## STDIO Deployment (Local/IDE)

STDIO transport is ideal for local development and IDE integration.

### 1. Environment Setup

Create `.env` file:

```bash
cp .env.example .env
```

Configure required variables:

```env
MULTILEAD_API_KEY=ml_live_your_api_key_here
TRANSPORT=stdio
LOG_LEVEL=INFO
```

### 2. Start Server

Using the start script:

```bash
./start.sh
```

Or manually:

```bash
source .venv/bin/activate
export TRANSPORT=stdio
python server.py
```

### 3. IDE Configuration

#### Claude Desktop

**Location:**
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

**Configuration:**

```json
{
  "mcpServers": {
    "multilead": {
      "command": "python",
      "args": [
        "/absolute/path/to/multilead-mcp/server.py"
      ],
      "env": {
        "MULTILEAD_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

**Alternative with script:**

```json
{
  "mcpServers": {
    "multilead": {
      "command": "/absolute/path/to/multilead-mcp/start.sh"
    }
  }
}
```

#### Cursor

**Location:** `.cursor/mcp_config.json` in your project

**Configuration:**

```json
{
  "mcpServers": {
    "multilead": {
      "command": "python",
      "args": [
        "/absolute/path/to/multilead-mcp/server.py"
      ],
      "env": {
        "MULTILEAD_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

#### Claude Code

**Location:** `.claude/mcp.json` in your project

**Configuration:**

```json
{
  "mcpServers": {
    "multilead": {
      "command": "python",
      "args": [
        "/absolute/path/to/multilead-mcp/server.py"
      ],
      "env": {
        "MULTILEAD_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

### 4. Verification

After configuration:

1. Restart your IDE/application
2. Check server logs for successful startup
3. Try using a Multilead tool (e.g., "list leads")

## HTTP Deployment (Remote Access)

HTTP transport enables remote access, team collaboration, and cloud deployment.

### 1. Local HTTP Server

For development and testing:

```bash
./start-http.sh
```

Server will be available at:
- MCP Endpoint: `http://localhost:8000/mcp`
- Health Check: `http://localhost:8000/health`

**Custom configuration:**

```bash
./start-http.sh --host 127.0.0.1 --port 3000 --log-level DEBUG
```

**Available options:**

- `--host HOST`: Bind address (default: 0.0.0.0)
- `--port PORT`: Port number (default: 8000)
- `--log-level LEVEL`: DEBUG, INFO, WARNING, ERROR, CRITICAL
- `--log-format FORMAT`: text or json
- `--production`: Enable production mode (JSON logs)

### 2. Client Configuration (HTTP)

Configure your MCP client to connect to the HTTP endpoint:

```json
{
  "mcpServers": {
    "multilead": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

### 3. Production Deployment

For production HTTP deployment, use a process manager and reverse proxy.

#### Using systemd

Create `/etc/systemd/system/multilead-mcp.service`:

```ini
[Unit]
Description=Multilead MCP Server
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/multilead-mcp
Environment="PATH=/opt/multilead-mcp/.venv/bin"
EnvironmentFile=/opt/multilead-mcp/.env
ExecStart=/opt/multilead-mcp/start-http.sh --production
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable and start:**

```bash
sudo systemctl daemon-reload
sudo systemctl enable multilead-mcp
sudo systemctl start multilead-mcp
sudo systemctl status multilead-mcp
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
COPY .env.example .env

# Expose port
EXPOSE 8000

# Set environment
ENV TRANSPORT=http
ENV HOST=0.0.0.0
ENV PORT=8000
ENV LOG_FORMAT=json

# Run server
CMD ["python", "server.py"]
```

**Build and run:**

```bash
docker build -t multilead-mcp .
docker run -p 8000:8000 -e MULTILEAD_API_KEY=your_key multilead-mcp
```

#### Using nginx Reverse Proxy

Configure nginx as reverse proxy:

```nginx
server {
    listen 80;
    server_name multilead-mcp.example.com;

    location /mcp {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /health {
        proxy_pass http://127.0.0.1:8000;
        access_log off;
    }
}
```

**With SSL (Let's Encrypt):**

```bash
sudo certbot --nginx -d multilead-mcp.example.com
```

## Production Configuration

### Environment Variables

Production `.env` configuration:

```env
# Required
MULTILEAD_API_KEY=ml_live_production_key_here
MULTILEAD_BASE_URL=https://api.multilead.co

# Transport
TRANSPORT=http
HOST=0.0.0.0
PORT=8000

# Logging (Production)
LOG_LEVEL=INFO
LOG_FORMAT=json

# Rate Limiting
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_PER_HOUR=1000

# Performance
MULTILEAD_TIMEOUT=30
```

### Security Best Practices

1. **Never commit `.env` files** - Use `.env.example` as template
2. **Use environment-specific API keys** - Different keys for dev/staging/prod
3. **Enable rate limiting** - Protect against abuse
4. **Use HTTPS in production** - SSL/TLS certificates required
5. **Restrict access** - Use firewall rules or authentication
6. **Rotate API keys regularly** - Update keys periodically
7. **Monitor logs** - Track errors and suspicious activity

### Production Checklist

Before deploying to production:

- [ ] API key configured (production key, not development)
- [ ] HTTPS/SSL certificate configured
- [ ] Rate limiting enabled
- [ ] Logging configured (JSON format)
- [ ] Log rotation configured
- [ ] Health check endpoint accessible
- [ ] Firewall rules configured
- [ ] Process manager configured (systemd/supervisor)
- [ ] Reverse proxy configured (nginx/caddy)
- [ ] Monitoring/alerting configured
- [ ] Backup strategy defined
- [ ] Documentation updated

## Monitoring and Logging

### Health Check Endpoint

The `/health` endpoint provides server status:

```bash
curl http://localhost:8000/health
```

**Response:**

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

**Status codes:**
- `200`: Healthy
- `503`: Unhealthy or degraded

### Logging

Logs are written to:
- **Console**: stdout/stderr (all transports)
- **File**: `logs/multilead-mcp.log` (HTTP transport only)

**Log formats:**

**Text format (development):**
```
2025-01-15 10:30:00 - multilead-mcp - INFO - Request completed: GET /mcp - Status: 200 - Duration: 0.123s
```

**JSON format (production):**
```json
{
  "timestamp": "2025-01-15T10:30:00Z",
  "level": "INFO",
  "logger": "multilead-mcp",
  "message": "Request completed: GET /mcp - Status: 200 - Duration: 0.123s",
  "module": "server",
  "function": "logging_middleware",
  "line": 367
}
```

**Log rotation:**
- Max file size: 10 MB
- Backup count: 5 files
- Total max size: ~50 MB

### Production Middleware Features

The server includes production-ready middleware:

1. **Request Logging**: All requests logged with timing
2. **Error Handling**: Graceful error responses
3. **Rate Limiting**: Configurable per-minute and per-hour limits
4. **Health Checks**: `/health` endpoint for monitoring
5. **Response Timing**: `X-Response-Time` header added

### Monitoring Integration

**Prometheus metrics** (future):
```python
# Request count
http_requests_total{method="POST",endpoint="/mcp",status="200"}

# Request duration
http_request_duration_seconds{method="POST",endpoint="/mcp"}

# Rate limit hits
rate_limit_hits_total{client_ip="1.2.3.4"}
```

**Sentry error tracking** (future):
```env
SENTRY_DSN=https://your-sentry-dsn
```

## Troubleshooting

### Server Won't Start

**Issue:** Server fails to start

**Check:**
1. Virtual environment activated
2. Dependencies installed: `pip install -e .`
3. `.env` file exists with valid API key
4. Port not already in use: `lsof -i :8000`
5. Python version 3.10+: `python --version`

### API Key Errors

**Issue:** Authentication failed

**Solutions:**
1. Verify API key in `.env` file
2. Check key is valid at https://app.multilead.co/settings/api
3. Ensure no extra spaces in `.env` file
4. Try regenerating API key

### Rate Limiting Issues

**Issue:** Getting 429 Too Many Requests

**Solutions:**
1. Increase limits in `.env`:
   ```env
   RATE_LIMIT_PER_MINUTE=200
   RATE_LIMIT_PER_HOUR=2000
   ```
2. Implement request queuing in client
3. Use multiple API keys with load balancing

### Connection Timeouts

**Issue:** Requests timing out

**Solutions:**
1. Increase timeout in `.env`:
   ```env
   MULTILEAD_TIMEOUT=60
   ```
2. Check network connectivity
3. Verify Multilead API status

### HTTP Transport Not Working

**Issue:** Can't connect to HTTP endpoint

**Check:**
1. Server started in HTTP mode: `TRANSPORT=http`
2. Correct host/port configuration
3. Firewall not blocking port
4. Client using correct URL: `http://host:port/mcp`

### STDIO Transport Not Working

**Issue:** IDE can't connect to server

**Check:**
1. Absolute path to `server.py` in config
2. Virtual environment properly configured
3. API key in environment variables
4. IDE/application restarted after config change
5. Check IDE logs for error messages

### Logs Not Appearing

**Issue:** No log files created

**Solutions:**
1. Logs only created in HTTP mode
2. Check `logs/` directory exists
3. Verify write permissions
4. Check LOG_LEVEL setting

### High Memory Usage

**Issue:** Server consuming too much memory

**Solutions:**
1. Rate limiter accumulating too many entries
2. Restart server periodically
3. Reduce RATE_LIMIT_PER_HOUR
4. Implement Redis-based rate limiting

## Getting Help

For issues with:
- **This server**: Check logs, review this documentation
- **Multilead API**: Contact [Multilead support](https://app.multilead.co/support)
- **FastMCP framework**: Visit [FastMCP documentation](https://gofastmcp.com)
- **Claude/MCP clients**: Check respective documentation

## Next Steps

- Review [IDE Setup Guide](../setup/IDE_SETUP.md)
- Check [Testing Guide](../testing/TESTING.md)
- See [Production Deployment Checklist](DEPLOYMENT_CHECKLIST.md)
- Read [Environment Variables Guide](../setup/ENVIRONMENT_VARIABLES.md)
