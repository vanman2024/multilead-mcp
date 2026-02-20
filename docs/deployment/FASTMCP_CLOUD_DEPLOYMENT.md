# FastMCP Cloud Deployment Guide

Complete guide for deploying the Multilead MCP Server to FastMCP Cloud.

## Overview

FastMCP Cloud provides managed hosting for MCP servers with automatic scaling, monitoring, and HTTPS endpoints. This guide provides the exact configuration needed to deploy the Multilead MCP Server.

---

## Prerequisites

1. **GitHub Repository**: Repository already exists at https://github.com/vanman2024/multilead-mcp
2. **FastMCP Cloud Account**: Sign up at https://cloud.fastmcp.com
3. **Multilead API Key**: Obtain from https://app.multilead.co/settings/api

---

## Deployment Configuration

### Server Information

- **Repository**: `https://github.com/vanman2024/multilead-mcp`
- **Server Entrypoint**: `server.py:mcp`
- **Python Version**: 3.10 or higher
- **Framework**: FastMCP 2.13.0+

### Required Files

All required files are already in the repository:

- ✅ `server.py` - Main server file with `mcp = FastMCP(...)` instance
- ✅ `pyproject.toml` - Python dependencies
- ✅ `fastmcp.json` - Server manifest and configuration
- ✅ `.gitignore` - Excludes `.env` files from git

---

## FastMCP Cloud Configuration

### Step-by-Step Deployment

#### 1. Visit FastMCP Cloud

Navigate to: **https://cloud.fastmcp.com**

#### 2. Sign In with GitHub

Click "Sign in with GitHub" and authorize FastMCP Cloud to access your repositories.

#### 3. Create New Project

Click **"New Project"** or **"Deploy New Server"**

#### 4. Select Repository

- **Organization/User**: `vanman2024`
- **Repository**: `multilead-mcp`
- **Branch**: `master` (or `main` if you renamed it)

#### 5. Configure Server Entrypoint

Enter the exact entrypoint:

```
server.py:mcp
```

**Format Explanation**:
- `server.py` - The file containing your FastMCP instance
- `mcp` - The variable name of your FastMCP instance (line 25 in server.py)

#### 6. Add Environment Variables

Add the following environment variables in the FastMCP Cloud dashboard:

##### Required Variables

```
MULTILEAD_API_KEY=your_multilead_api_key_here
```

**How to get your API key**:
1. Visit https://app.multilead.co/settings/api
2. Copy your API key
3. Paste it as the value for `MULTILEAD_API_KEY`

##### Optional Variables (with defaults)

```
MULTILEAD_BASE_URL=https://api.multilead.co
MULTILEAD_TIMEOUT=30
MULTILEAD_DEBUG=false
TRANSPORT=http
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO
LOG_FORMAT=json
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_PER_HOUR=1000
```

**Recommended Production Values**:

```
MULTILEAD_API_KEY=your_multilead_api_key_here
TRANSPORT=http
LOG_LEVEL=INFO
LOG_FORMAT=json
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_PER_HOUR=1000
```

#### 7. Deploy

Click **"Deploy"** to start the deployment process.

---

## Post-Deployment

### Expected Deployment URL

Your server will be available at:

```
https://multilead-mcp.fastmcp.app/mcp
```

**Note**: The exact subdomain may vary. Check your FastMCP Cloud dashboard for the actual URL.

### Available Endpoints

Once deployed, you'll have access to:

- **MCP Endpoint**: `https://multilead-mcp.fastmcp.app/mcp`
- **Health Check**: `https://multilead-mcp.fastmcp.app/health`

---

## Verification

### 1. Monitor Deployment Logs

In the FastMCP Cloud dashboard:
1. Navigate to your project
2. Click on **"Logs"** tab
3. Watch for successful startup messages

Expected log output:
```
INFO - Starting Multilead Open API Server
INFO - Transport: http
INFO - Server started successfully
```

### 2. Test Health Endpoint

Once deployment is complete, test the health endpoint:

```bash
curl https://multilead-mcp.fastmcp.app/health
```

**Expected Response** (200 OK):
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

### 3. Test MCP Endpoint

Test the MCP endpoint with a simple request:

```bash
curl -X POST https://multilead-mcp.fastmcp.app/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/list",
    "id": 1
  }'
```

**Expected Response**: List of 77 available tools

---

## IDE Integration

### Claude Desktop Configuration

Once deployed, configure Claude Desktop to use your FastMCP Cloud deployment:

**File Location**:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

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

### Claude Code Configuration

**File**: `.claude/mcp.json` (in your project directory)

```json
{
  "mcpServers": {
    "multilead": {
      "url": "https://multilead-mcp.fastmcp.app/mcp"
    }
  }
}
```

### Cursor Configuration

**File**: `.cursor/mcp_config.json` (in your project directory)

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

## Environment Variables Reference

### Required Variables

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `MULTILEAD_API_KEY` | Your Multilead API key from https://app.multilead.co/settings/api | `ml_live_abc123...` | Yes |

### Optional API Variables

| Variable | Default | Description | Required |
|----------|---------|-------------|----------|
| `MULTILEAD_BASE_URL` | `https://api.multilead.co` | Multilead API base URL | No |
| `MULTILEAD_TIMEOUT` | `30` | Request timeout in seconds | No |
| `MULTILEAD_DEBUG` | `false` | Enable debug logging | No |

### Optional Server Variables

| Variable | Default | Description | Required |
|----------|---------|-------------|----------|
| `TRANSPORT` | `stdio` | Transport mode (`stdio` or `http`) | No (use `http` for cloud) |
| `HOST` | `0.0.0.0` | HTTP server host | No |
| `PORT` | `8000` | HTTP server port | No |
| `LOG_LEVEL` | `INFO` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`) | No |
| `LOG_FORMAT` | `text` | Log format (`text` or `json`) | No (use `json` for cloud) |
| `RATE_LIMIT_PER_MINUTE` | `100` | Maximum requests per minute | No |
| `RATE_LIMIT_PER_HOUR` | `1000` | Maximum requests per hour | No |

---

## Updating the Deployment

### Code Updates

FastMCP Cloud automatically redeploys when you push changes to your GitHub repository:

1. Make changes to your code locally
2. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "Update server code"
   git push origin master
   ```
3. FastMCP Cloud will automatically detect the change and redeploy

### Environment Variable Updates

To update environment variables:

1. Log in to https://cloud.fastmcp.com
2. Navigate to your project
3. Go to **Settings** → **Environment Variables**
4. Update the variables
5. Click **"Redeploy"** to apply changes

---

## Monitoring and Logs

### Viewing Logs

**In FastMCP Cloud Dashboard**:
1. Navigate to your project
2. Click on **"Logs"** tab
3. View real-time logs or filter by time range

**Log Levels**:
- `DEBUG` - Detailed debugging information (development only)
- `INFO` - General informational messages (recommended for production)
- `WARNING` - Warning messages that don't prevent operation
- `ERROR` - Error messages for failed operations
- `CRITICAL` - Critical errors that may cause service disruption

### Health Monitoring

Set up health check monitoring:

**Health Endpoint**: `https://multilead-mcp.fastmcp.app/health`

**Monitoring Services**:
- UptimeRobot: https://uptimerobot.com
- Pingdom: https://www.pingdom.com
- StatusCake: https://www.statuscake.com

**Configuration**:
- **URL**: `https://multilead-mcp.fastmcp.app/health`
- **Method**: GET
- **Expected Status**: 200 OK
- **Check Interval**: 1-5 minutes
- **Alert On**: Status code != 200 or timeout

---

## Troubleshooting

### Deployment Failed

**Check deployment logs**:
1. Go to FastMCP Cloud dashboard
2. Navigate to your project
3. Click **"Logs"** tab
4. Look for error messages

**Common Issues**:

1. **Missing dependencies**: Ensure all dependencies are in `pyproject.toml`
2. **Wrong entrypoint**: Verify `server.py:mcp` is correct
3. **Python version**: Ensure `requires-python = ">=3.10"` in `pyproject.toml`

### Health Check Failing

**Test the endpoint**:
```bash
curl -v https://multilead-mcp.fastmcp.app/health
```

**Common Issues**:

1. **Missing API key**: Add `MULTILEAD_API_KEY` in environment variables
2. **Invalid API key**: Verify key is correct at https://app.multilead.co/settings/api
3. **Server not started**: Check deployment logs for startup errors

**Expected Healthy Response** (200 OK):
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

**Unhealthy Response** (503 Service Unavailable):
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

### MCP Tools Not Working

**Check tool availability**:
```bash
curl -X POST https://multilead-mcp.fastmcp.app/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/list",
    "id": 1
  }'
```

**Expected**: List of 77 tools

**Common Issues**:

1. **Server error**: Check logs for Python exceptions
2. **API connection**: Verify Multilead API is accessible
3. **Rate limiting**: Check if you've exceeded rate limits

### Rate Limiting

If you receive `429 Too Many Requests`:

1. **Wait**: Rate limits reset after the time period (per minute/hour)
2. **Adjust limits**: Update `RATE_LIMIT_PER_MINUTE` and `RATE_LIMIT_PER_HOUR` environment variables
3. **Check logs**: Verify rate limit configuration in deployment logs

**Default Limits**:
- 100 requests per minute
- 1000 requests per hour

**Increase Limits** (example):
```
RATE_LIMIT_PER_MINUTE=500
RATE_LIMIT_PER_HOUR=5000
```

---

## Security Considerations

### API Key Protection

**Never commit API keys to git**:
- ✅ `.env` files are in `.gitignore`
- ✅ Use environment variables in FastMCP Cloud
- ✅ API keys are never logged or exposed

**API Key Rotation**:
1. Generate new key at https://app.multilead.co/settings/api
2. Update `MULTILEAD_API_KEY` in FastMCP Cloud environment variables
3. Click **"Redeploy"**
4. Revoke old key in Multilead dashboard

### HTTPS/SSL

FastMCP Cloud automatically provides:
- ✅ SSL/TLS certificates
- ✅ HTTPS endpoints
- ✅ Automatic certificate renewal

### Rate Limiting

Rate limiting is automatically enabled to prevent abuse:
- Per-client IP tracking
- Configurable limits
- 429 status code with `Retry-After` header

---

## Performance Optimization

### Recommended Settings for Production

```
MULTILEAD_TIMEOUT=60
LOG_LEVEL=INFO
LOG_FORMAT=json
RATE_LIMIT_PER_MINUTE=500
RATE_LIMIT_PER_HOUR=5000
```

### Monitoring Metrics

Track these key metrics:
- **Health endpoint uptime**: Should be >99.9%
- **Response time**: Health endpoint latency (target: <100ms)
- **Error rate**: Failed requests to Multilead API (target: <1%)
- **Rate limit hits**: 429 responses (should be minimal)

---

## Cost Considerations

FastMCP Cloud pricing is based on:
- Compute hours
- Data transfer
- Number of requests

**Recommendations**:
1. Start with default rate limits
2. Monitor usage in FastMCP Cloud dashboard
3. Adjust rate limits based on actual needs
4. Use health checks sparingly (5-minute intervals)

---

## Support

### FastMCP Cloud Support
- **Dashboard**: https://cloud.fastmcp.com
- **Documentation**: https://gofastmcp.com/deployment/fastmcp-cloud
- **Support**: support@fastmcp.com

### Multilead API Support
- **Dashboard**: https://app.multilead.co
- **Documentation**: https://docs.multilead.co
- **Support**: https://app.multilead.co/support

### Server Repository
- **GitHub**: https://github.com/vanman2024/multilead-mcp
- **Issues**: https://github.com/vanman2024/multilead-mcp/issues

---

## Quick Reference

### Deployment Checklist

- [ ] FastMCP Cloud account created
- [ ] GitHub repository connected
- [ ] Server entrypoint configured: `server.py:mcp`
- [ ] Environment variables added (at minimum: `MULTILEAD_API_KEY`)
- [ ] Deployment initiated
- [ ] Health endpoint tested: `https://multilead-mcp.fastmcp.app/health`
- [ ] MCP endpoint tested: `https://multilead-mcp.fastmcp.app/mcp`
- [ ] IDE configuration updated with deployment URL
- [ ] Health monitoring configured
- [ ] Documentation reviewed

### Key URLs

- **FastMCP Cloud Dashboard**: https://cloud.fastmcp.com
- **GitHub Repository**: https://github.com/vanman2024/multilead-mcp
- **Multilead API Settings**: https://app.multilead.co/settings/api
- **Multilead API Docs**: https://docs.multilead.co
- **FastMCP Documentation**: https://gofastmcp.com

### Copy-Paste Configuration

```
Repository: https://github.com/vanman2024/multilead-mcp
Server Entrypoint: server.py:mcp
Branch: master

Required Environment Variables:
  MULTILEAD_API_KEY=your_multilead_api_key_here

Recommended Environment Variables:
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

## Next Steps

1. **Deploy to FastMCP Cloud**: Follow the step-by-step guide above
2. **Configure IDE**: Update your IDE configuration with the deployment URL
3. **Test Tools**: Verify all 77 tools are working correctly
4. **Set Up Monitoring**: Configure health check monitoring
5. **Review Logs**: Monitor deployment logs for any issues

---

**Deployment configuration ready!** Follow the steps above to deploy to FastMCP Cloud.
