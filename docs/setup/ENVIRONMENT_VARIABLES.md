# Environment Variables Guide

Complete reference for all environment variables used by the Multilead MCP Server.

## Table of Contents

- [Quick Reference](#quick-reference)
- [Required Variables](#required-variables)
- [Multilead API Configuration](#multilead-api-configuration)
- [Transport Configuration](#transport-configuration)
- [Logging Configuration](#logging-configuration)
- [Rate Limiting Configuration](#rate-limiting-configuration)
- [Environment-Specific Configurations](#environment-specific-configurations)
- [Security Best Practices](#security-best-practices)

## Quick Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `MULTILEAD_API_KEY` | ✅ Yes | - | Your Multilead API key |
| `MULTILEAD_BASE_URL` | ❌ No | `https://api.multilead.co` | Multilead API base URL |
| `MULTILEAD_TIMEOUT` | ❌ No | `30` | Request timeout in seconds |
| `MULTILEAD_DEBUG` | ❌ No | `false` | Enable debug mode |
| `TRANSPORT` | ❌ No | `stdio` | Transport mode (stdio/http) |
| `HOST` | ❌ No | `0.0.0.0` | HTTP server host |
| `PORT` | ❌ No | `8000` | HTTP server port |
| `LOG_LEVEL` | ❌ No | `INFO` | Logging level |
| `LOG_FORMAT` | ❌ No | `text` | Log format (text/json) |
| `RATE_LIMIT_PER_MINUTE` | ❌ No | `100` | Requests per minute limit |
| `RATE_LIMIT_PER_HOUR` | ❌ No | `1000` | Requests per hour limit |

## Required Variables

### MULTILEAD_API_KEY

**Required:** Yes  
**Format:** String (API key)  
**Example:** `ml_live_abc123xyz456`

Your Multilead API authentication key.

**How to obtain:**
1. Login to https://app.multilead.co
2. Navigate to Settings → API
3. Create or copy your API key

**Usage:**
```env
MULTILEAD_API_KEY=ml_live_abc123xyz456
```

**Security:**
- Never commit this to git
- Use different keys for dev/staging/production
- Rotate keys periodically
- Store in secure secrets manager for production

## Multilead API Configuration

### MULTILEAD_BASE_URL

**Required:** No  
**Default:** `https://api.multilead.co`  
**Format:** URL

The base URL for the Multilead API.

**Usage:**
```env
MULTILEAD_BASE_URL=https://api.multilead.co
```

**When to change:**
- Using a different Multilead environment
- Testing with a staging API
- Using a proxy or API gateway

### MULTILEAD_TIMEOUT

**Required:** No  
**Default:** `30`  
**Format:** Integer (seconds)

Maximum time to wait for API responses.

**Usage:**
```env
MULTILEAD_TIMEOUT=30
```

**Recommendations:**
- Development: `30` seconds
- Production: `30-60` seconds
- Slow networks: `60-120` seconds

**Too low:** Requests may timeout prematurely  
**Too high:** Slow responses block other operations

### MULTILEAD_DEBUG

**Required:** No  
**Default:** `false`  
**Format:** Boolean (`true`/`false`)

Enable additional debug logging for Multilead API requests.

**Usage:**
```env
MULTILEAD_DEBUG=true
```

**When to enable:**
- Debugging API issues
- Troubleshooting request/response problems
- Development and testing

**When to disable:**
- Production deployments (security)
- Performance-sensitive applications
- To reduce log noise

## Transport Configuration

### TRANSPORT

**Required:** No  
**Default:** `stdio`  
**Format:** String (`stdio` or `http`)

The transport mode for the MCP server.

**Usage:**
```env
TRANSPORT=stdio  # For IDE integration
TRANSPORT=http   # For HTTP server
```

**Modes:**

**STDIO** (Standard Input/Output):
- For Claude Desktop, Cursor, Claude Code
- Local process communication
- No network required
- Default for IDE integration

**HTTP**:
- For remote access
- Web services
- Cloud deployment
- Team collaboration

### HOST

**Required:** No  
**Default:** `0.0.0.0`  
**Format:** IP address or hostname

HTTP server bind address (only for `TRANSPORT=http`).

**Usage:**
```env
HOST=0.0.0.0      # All interfaces (default)
HOST=127.0.0.1    # Localhost only
HOST=192.168.1.10 # Specific interface
```

**Recommendations:**
- Development: `127.0.0.1` (localhost only)
- Production: `0.0.0.0` (all interfaces with firewall)
- Security: Use reverse proxy instead of direct binding

### PORT

**Required:** No  
**Default:** `8000`  
**Format:** Integer (1-65535)

HTTP server port (only for `TRANSPORT=http`).

**Usage:**
```env
PORT=8000   # Default
PORT=3000   # Custom port
```

**Recommendations:**
- Development: Any available port (3000, 8000, 8080)
- Production: Standard ports behind reverse proxy
- Avoid: Privileged ports (<1024) require root

## Logging Configuration

### LOG_LEVEL

**Required:** No  
**Default:** `INFO`  
**Format:** String

Logging verbosity level.

**Valid values:**
- `DEBUG` - Very detailed, includes all operations
- `INFO` - Normal operations and important events
- `WARNING` - Warnings and potential issues
- `ERROR` - Errors that don't stop execution
- `CRITICAL` - Critical errors requiring attention

**Usage:**
```env
LOG_LEVEL=INFO
```

**Recommendations:**
- Development: `DEBUG` or `INFO`
- Production: `INFO` or `WARNING`
- Troubleshooting: `DEBUG`

**Log output by level:**

```
DEBUG:    All requests, responses, operations
INFO:     Request completion, tool execution
WARNING:  Rate limits, deprecations, unusual behavior
ERROR:    API errors, timeouts, failures
CRITICAL: Server crashes, unrecoverable errors
```

### LOG_FORMAT

**Required:** No  
**Default:** `text`  
**Format:** String (`text` or `json`)

Log message format.

**Usage:**
```env
LOG_FORMAT=text  # Human-readable
LOG_FORMAT=json  # Machine-readable
```

**Text format** (development):
```
2025-01-15 10:30:00 - multilead-mcp - INFO - Request completed: GET /mcp
```

**JSON format** (production):
```json
{
  "timestamp": "2025-01-15T10:30:00Z",
  "level": "INFO",
  "message": "Request completed: GET /mcp"
}
```

**Recommendations:**
- Development: `text` (easier to read)
- Production: `json` (easier to parse and analyze)
- Log aggregation: `json` (for ELK, Splunk, Datadog)

## Rate Limiting Configuration

Rate limiting is only active when `TRANSPORT=http`.

### RATE_LIMIT_PER_MINUTE

**Required:** No  
**Default:** `100`  
**Format:** Integer (requests per minute)

Maximum requests allowed per minute per client IP.

**Usage:**
```env
RATE_LIMIT_PER_MINUTE=100
```

**Recommendations:**
- Light usage: `50-100`
- Moderate usage: `100-200`
- Heavy usage: `200-500`
- No limit: Set very high (e.g., `10000`)

**Exceeded:** Client receives `429 Too Many Requests`

### RATE_LIMIT_PER_HOUR

**Required:** No  
**Default:** `1000`  
**Format:** Integer (requests per hour)

Maximum requests allowed per hour per client IP.

**Usage:**
```env
RATE_LIMIT_PER_HOUR=1000
```

**Recommendations:**
- Light usage: `500-1000`
- Moderate usage: `1000-2000`
- Heavy usage: `2000-5000`
- No limit: Set very high (e.g., `100000`)

**Note:** Both per-minute and per-hour limits are enforced. If either limit is exceeded, requests are blocked.

## Environment-Specific Configurations

### Development

Create `.env.development`:

```env
# Multilead API
MULTILEAD_API_KEY=ml_test_development_key_here
MULTILEAD_BASE_URL=https://api.multilead.co
MULTILEAD_TIMEOUT=30
MULTILEAD_DEBUG=true

# Transport
TRANSPORT=stdio

# Logging
LOG_LEVEL=DEBUG
LOG_FORMAT=text
```

**Usage:**
```bash
cp .env.development .env
```

### Staging

Create `.env.staging`:

```env
# Multilead API
MULTILEAD_API_KEY=ml_test_staging_key_here
MULTILEAD_BASE_URL=https://api.multilead.co
MULTILEAD_TIMEOUT=30
MULTILEAD_DEBUG=false

# Transport
TRANSPORT=http
HOST=0.0.0.0
PORT=8000

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Rate Limiting
RATE_LIMIT_PER_MINUTE=200
RATE_LIMIT_PER_HOUR=2000
```

### Production

Create `.env.production`:

```env
# Multilead API
MULTILEAD_API_KEY=ml_live_production_key_here
MULTILEAD_BASE_URL=https://api.multilead.co
MULTILEAD_TIMEOUT=30
MULTILEAD_DEBUG=false

# Transport
TRANSPORT=http
HOST=0.0.0.0
PORT=8000

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Rate Limiting
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_PER_HOUR=1000
```

**Deploy to production:**
```bash
cp .env.production .env
# Or set environment variables directly in your deployment system
```

## Security Best Practices

### 1. Never Commit Secrets

**Always gitignore:**
```gitignore
.env
.env.*
!.env.example
*.key
credentials.json
```

**Use `.env.example` for documentation:**
```env
MULTILEAD_API_KEY=your_multilead_api_key_here
```

### 2. Use Different Keys Per Environment

- Development: Test data, development key
- Staging: Production-like, staging key
- Production: Real data, production key

**Benefits:**
- Isolate environments
- Limit blast radius of key leaks
- Easy to rotate compromised keys

### 3. Rotate Keys Regularly

**Recommended schedule:**
- Every 90 days for production
- After team member departure
- After suspected compromise
- For compliance requirements

**Rotation process:**
1. Generate new key in Multilead dashboard
2. Update `.env` file or secrets manager
3. Restart server
4. Verify functionality
5. Revoke old key

### 4. Use Secrets Manager in Production

Instead of `.env` files, use:

**AWS Secrets Manager:**
```python
import boto3
secret = boto3.client('secretsmanager').get_secret_value(
    SecretId='multilead-api-key'
)
```

**HashiCorp Vault:**
```bash
export MULTILEAD_API_KEY=$(vault kv get -field=api_key secret/multilead)
```

**Environment variables (Docker/K8s):**
```yaml
env:
  - name: MULTILEAD_API_KEY
    valueFrom:
      secretKeyRef:
        name: multilead-secrets
        key: api-key
```

### 5. Minimize Variable Scope

**In IDE configs:**
```json
{
  "env": {
    "MULTILEAD_API_KEY": "key_here"
  }
}
```

**Not in shell profile:**
```bash
# DON'T do this in ~/.bashrc
export MULTILEAD_API_KEY=key_here  # Visible to all processes
```

### 6. Audit Access

**Log all API key usage:**
- Who accessed which environment
- When keys were used
- What operations performed

**Monitor for:**
- Unusual access patterns
- Failed authentication attempts
- Rate limit violations

## Troubleshooting

### Variable Not Loading

**Issue:** Environment variable not being used

**Solutions:**

1. **Check `.env` file exists:**
   ```bash
   ls -la .env
   ```

2. **Verify `.env` syntax:**
   ```env
   # Correct
   MULTILEAD_API_KEY=abc123
   
   # Incorrect (no spaces around =)
   MULTILEAD_API_KEY = abc123
   ```

3. **Check variable is exported (if not using .env file):**
   ```bash
   echo $MULTILEAD_API_KEY
   ```

4. **Restart server after changes**

### API Key Not Working

**Issue:** Authentication failed with correct key

**Solutions:**

1. **Check for whitespace:**
   ```bash
   # Remove any spaces
   MULTILEAD_API_KEY=abc123  # No spaces
   ```

2. **Verify key is active:**
   - Login to Multilead dashboard
   - Check API keys page
   - Ensure key not revoked

3. **Check key format:**
   - Should start with `ml_live_` or `ml_test_`
   - No quotes in `.env` file

### Override Not Working

**Issue:** Environment variable override not taking effect

**Solutions:**

1. **Export before running:**
   ```bash
   export LOG_LEVEL=DEBUG
   python server.py
   ```

2. **Use inline:**
   ```bash
   LOG_LEVEL=DEBUG python server.py
   ```

3. **Check load order:**
   - Command line > .env file > defaults

## Next Steps

- [Deployment Guide](../deployment/DEPLOYMENT.md)
- [IDE Setup Guide](IDE_SETUP.md)
- [Security Best Practices](../deployment/DEPLOYMENT_CHECKLIST.md)
