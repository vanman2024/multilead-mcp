# Quick Deployment Reference

Ultra-fast deployment guide for the Multilead MCP Server.

## 5-Minute Setup

### For Claude Desktop (STDIO)

```bash
# 1. Install
cd /home/gotime2022/Projects/mcp-servers/multilead-mcp
pip install -e .

# 2. Configure
cp .env.example .env
nano .env  # Add MULTILEAD_API_KEY=your_key_here

# 3. Test
./start.sh

# 4. Add to Claude Desktop
cp docs/setup/claude-desktop-config.json ~/Library/Application\ Support/Claude/claude_desktop_config.json
nano ~/Library/Application\ Support/Claude/claude_desktop_config.json  # Edit path and API key

# 5. Restart Claude Desktop
```

### For HTTP Server (Remote Access)

```bash
# 1. Install
cd /home/gotime2022/Projects/mcp-servers/multilead-mcp
pip install -e .

# 2. Configure
cp .env.example .env
nano .env  # Add MULTILEAD_API_KEY=your_key_here

# 3. Start
./start-http.sh

# 4. Test
curl http://localhost:8000/health
```

## Configuration Files Location

```
multilead-mcp/
├── .env                              # Your configuration (create from .env.example)
├── start.sh                          # STDIO startup
├── start-http.sh                     # HTTP startup
└── docs/
    ├── deployment/
    │   ├── DEPLOYMENT.md            # Full guide
    │   ├── DEPLOYMENT_CHECKLIST.md  # Checklist
    │   ├── DEPLOYMENT_SUMMARY.md    # Summary
    │   └── .env.production          # Production template
    └── setup/
        ├── IDE_SETUP.md             # IDE integration
        ├── ENVIRONMENT_VARIABLES.md # All variables
        └── *.json                   # IDE config templates
```

## Quick Commands

```bash
# STDIO mode (Claude Desktop/Code/Cursor)
./start.sh

# HTTP mode (default: localhost:8000)
./start-http.sh

# HTTP with custom port
./start-http.sh --port 3000

# Production mode (JSON logs)
./start-http.sh --production

# Debug mode
./start-http.sh --log-level DEBUG

# Health check
curl http://localhost:8000/health
```

## Environment Variables (Quick Reference)

**Required:**
```env
MULTILEAD_API_KEY=your_api_key_here
```

**Optional (with defaults):**
```env
TRANSPORT=stdio              # or "http"
HOST=0.0.0.0                # HTTP host
PORT=8000                   # HTTP port
LOG_LEVEL=INFO              # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT=text             # or "json" for production
RATE_LIMIT_PER_MINUTE=100   # Requests per minute
RATE_LIMIT_PER_HOUR=1000    # Requests per hour
```

## IDE Configuration (Quick)

### Claude Desktop

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Linux:** `~/.config/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "multilead": {
      "command": "python",
      "args": ["/absolute/path/to/multilead-mcp/server.py"],
      "env": {
        "MULTILEAD_API_KEY": "your_key_here"
      }
    }
  }
}
```

### Cursor

**.cursor/mcp_config.json** in your project:

```json
{
  "mcpServers": {
    "multilead": {
      "command": "python",
      "args": ["/absolute/path/to/multilead-mcp/server.py"],
      "env": {
        "MULTILEAD_API_KEY": "your_key_here"
      }
    }
  }
}
```

### Claude Code

**.claude/mcp.json** in your project:

```json
{
  "mcpServers": {
    "multilead": {
      "command": "python",
      "args": ["/absolute/path/to/multilead-mcp/server.py"],
      "env": {
        "MULTILEAD_API_KEY": "your_key_here"
      }
    }
  }
}
```

## Production Deployment

```bash
# 1. Copy production config
cp docs/deployment/.env.production .env
nano .env  # Add production API key

# 2. Start in production mode
./start-http.sh --production

# 3. Verify health
curl http://localhost:8000/health

# 4. Configure systemd (optional)
# See docs/deployment/DEPLOYMENT.md for systemd setup
```

## Troubleshooting (Quick)

**Server won't start:**
```bash
python --version           # Check Python 3.10+
pip install -e .          # Reinstall dependencies
cat .env                  # Check API key configured
```

**API key errors:**
```bash
# Verify key at https://app.multilead.co/settings/api
echo $MULTILEAD_API_KEY   # Check if set
```

**Port already in use:**
```bash
./start-http.sh --port 3000  # Use different port
lsof -i :8000                # Find what's using port
```

**IDE not connecting:**
```bash
# 1. Use absolute paths (not ~/...)
# 2. Restart IDE completely
# 3. Check IDE logs
# 4. Test manually: python /path/to/server.py
```

## Need More Help?

- **Full deployment guide**: [docs/deployment/DEPLOYMENT.md](DEPLOYMENT.md)
- **IDE setup guide**: [docs/setup/IDE_SETUP.md](../setup/IDE_SETUP.md)
- **All environment variables**: [docs/setup/ENVIRONMENT_VARIABLES.md](../setup/ENVIRONMENT_VARIABLES.md)
- **Deployment checklist**: [docs/deployment/DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)

## Support

- **Multilead API**: https://app.multilead.co/support
- **FastMCP**: https://gofastmcp.com

---

**That's it!** Server is ready to deploy. 🚀
