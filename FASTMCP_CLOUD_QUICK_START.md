# FastMCP Cloud Quick Start

Quick reference for deploying Multilead MCP Server to FastMCP Cloud.

---

## Copy-Paste Configuration

Use these exact values when deploying to FastMCP Cloud:

```
╔════════════════════════════════════════════════════════════╗
║          FastMCP Cloud Deployment Configuration           ║
╚════════════════════════════════════════════════════════════╝

GitHub Repository: https://github.com/vanman2024/multilead-mcp
Server Entrypoint: server.py:mcp
Branch: master

Required Environment Variables:
  MULTILEAD_API_KEY=your_multilead_api_key_here

Optional Environment Variables (Recommended for Production):
  TRANSPORT=http
  LOG_LEVEL=INFO
  LOG_FORMAT=json
  RATE_LIMIT_PER_MINUTE=100
  RATE_LIMIT_PER_HOUR=1000

Expected Deployment URL:
  https://multilead-mcp.fastmcp.app/mcp

Health Check URL:
  https://multilead-mcp.fastmcp.app/health
```

---

## Step-by-Step Deployment

### 1. Visit FastMCP Cloud
Navigate to: **https://cloud.fastmcp.com**

### 2. Sign In with GitHub
Click "Sign in with GitHub" and authorize access.

### 3. Create New Project
Click **"New Project"** or **"Deploy New Server"**

### 4. Select Repository
- **User**: `vanman2024`
- **Repository**: `multilead-mcp`
- **Branch**: `master`

### 5. Configure Server Entrypoint
Enter exactly:
```
server.py:mcp
```

### 6. Add Environment Variables

**Minimum Required**:
```
MULTILEAD_API_KEY=your_multilead_api_key_here
```

Get your API key from: https://app.multilead.co/settings/api

**Recommended Additional Variables**:
```
TRANSPORT=http
LOG_LEVEL=INFO
LOG_FORMAT=json
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_PER_HOUR=1000
```

### 7. Deploy
Click **"Deploy"** and wait for deployment to complete.

---

## Verification

### Test Health Endpoint
```bash
curl https://multilead-mcp.fastmcp.app/health
```

**Expected Response** (200 OK):
```json
{
  "status": "healthy",
  "service": "multilead-mcp",
  "version": "1.0.0",
  "transport": "http",
  "api_configured": true
}
```

### Test MCP Endpoint
```bash
curl -X POST https://multilead-mcp.fastmcp.app/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/list",
    "id": 1
  }'
```

**Expected**: List of 77 available tools

---

## IDE Configuration

### Claude Desktop

**Location**:
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

**Configuration**:
```json
{
  "mcpServers": {
    "multilead": {
      "url": "https://multilead-mcp.fastmcp.app/mcp"
    }
  }
}
```

### Claude Code

**File**: `.claude/mcp.json`

```json
{
  "mcpServers": {
    "multilead": {
      "url": "https://multilead-mcp.fastmcp.app/mcp"
    }
  }
}
```

### Cursor

**File**: `.cursor/mcp_config.json`

```json
{
  "mcpServers": {
    "multilead": {
      "url": "https://multilead-mcp.fastmcp.app/mcp"
    }
  }
}
```

---

## Key Information

### Server Details
- **Tools**: 77 tools for lead management, campaigns, conversations, webhooks
- **Resources**: 2 resources (system info, API stats)
- **Prompts**: 2 prompts (lead generation, campaign management)
- **Python Version**: 3.10+
- **FastMCP Version**: 2.13.0+

### API Key
Get your Multilead API key from:
**https://app.multilead.co/settings/api**

### Rate Limits
- Default: 100 requests/minute, 1000 requests/hour
- Configurable via environment variables
- Returns 429 status code when exceeded

### Logging
- Format: JSON (production) or text (development)
- Levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Default: INFO level, JSON format for cloud deployment

---

## Troubleshooting

### Deployment Failed
1. Check logs in FastMCP Cloud dashboard
2. Verify `server.py:mcp` entrypoint is correct
3. Ensure all dependencies in `pyproject.toml`

### Health Check Failing
1. Verify `MULTILEAD_API_KEY` is set correctly
2. Get new API key from https://app.multilead.co/settings/api
3. Check deployment logs for startup errors

### Tools Not Working
1. Test with `curl` to `/mcp` endpoint
2. Verify Multilead API key is valid
3. Check rate limits haven't been exceeded

---

## Support

- **Full Documentation**: `docs/deployment/FASTMCP_CLOUD_DEPLOYMENT.md`
- **FastMCP Cloud**: https://cloud.fastmcp.com
- **Multilead API**: https://app.multilead.co/support
- **GitHub Issues**: https://github.com/vanman2024/multilead-mcp/issues

---

## Deployment Checklist

- [ ] FastMCP Cloud account created
- [ ] Multilead API key obtained
- [ ] Repository: `vanman2024/multilead-mcp` selected
- [ ] Entrypoint: `server.py:mcp` configured
- [ ] Environment variable `MULTILEAD_API_KEY` added
- [ ] Deployment initiated
- [ ] Health endpoint returns 200 OK
- [ ] MCP endpoint returns tool list
- [ ] IDE configured with deployment URL
- [ ] Health monitoring configured (optional)

---

**Ready to deploy!** Follow the steps above to get your Multilead MCP Server running on FastMCP Cloud.
