# IDE Integration Setup Guide

Complete guide for integrating the Multilead MCP Server with Claude Desktop, Cursor, and Claude Code.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Claude Desktop](#claude-desktop)
- [Cursor](#cursor)
- [Claude Code](#claude-code)
- [Troubleshooting](#troubleshooting)

## Prerequisites

Before setting up IDE integration:

1. **Python 3.10+** installed
2. **Server installed** with dependencies: `pip install -e .`
3. **API key** from https://app.multilead.co/settings/api
4. **Environment configured** with `.env` file

## Claude Desktop

Claude Desktop uses STDIO transport for local MCP servers.

### 1. Locate Configuration File

The configuration file location depends on your operating system:

**macOS:**
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Windows:**
```
%APPDATA%\Claude\claude_desktop_config.json
```
(Usually: `C:\Users\YourUsername\AppData\Roaming\Claude\claude_desktop_config.json`)

**Linux:**
```
~/.config/Claude/claude_desktop_config.json
```

### 2. Add Server Configuration

Open the configuration file and add the Multilead server:

```json
{
  "mcpServers": {
    "multilead": {
      "command": "python",
      "args": [
        "/absolute/path/to/multilead-mcp/server.py"
      ],
      "env": {
        "MULTILEAD_API_KEY": "your_multilead_api_key_here",
        "MULTILEAD_BASE_URL": "https://api.multilead.co",
        "TRANSPORT": "stdio",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

**Important:**
- Use absolute paths (not relative like `~/` or `./`)
- Replace `your_multilead_api_key_here` with your actual API key
- On Windows, use forward slashes: `C:/Users/...` or escape backslashes: `C:\\Users\\...`

### 3. Alternative: Using Start Script

You can also use the start script:

```json
{
  "mcpServers": {
    "multilead": {
      "command": "/absolute/path/to/multilead-mcp/start.sh"
    }
  }
}
```

This requires:
- `.env` file configured in the server directory
- Script has execute permissions: `chmod +x start.sh`

### 4. Restart Claude Desktop

After saving the configuration:

1. Quit Claude Desktop completely
2. Reopen Claude Desktop
3. Wait for server to initialize (~5 seconds)

### 5. Verify Integration

In Claude Desktop:

1. Look for MCP server indicator
2. Type: "List available Multilead tools"
3. Try: "Show me my Multilead leads"

Expected response should list available tools or leads.

## Cursor

Cursor supports MCP servers through a configuration file in your project.

### 1. Create Configuration Directory

In your project root:

```bash
mkdir -p .cursor
```

### 2. Create MCP Configuration

Create `.cursor/mcp_config.json`:

```json
{
  "mcpServers": {
    "multilead": {
      "command": "python",
      "args": [
        "/absolute/path/to/multilead-mcp/server.py"
      ],
      "env": {
        "MULTILEAD_API_KEY": "your_multilead_api_key_here",
        "MULTILEAD_BASE_URL": "https://api.multilead.co",
        "TRANSPORT": "stdio",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### 3. Project-Specific Configuration

For project-specific settings, add to your workspace settings (`.vscode/settings.json`):

```json
{
  "mcp.servers": {
    "multilead": {
      "command": "python",
      "args": [
        "/absolute/path/to/multilead-mcp/server.py"
      ],
      "env": {
        "MULTILEAD_API_KEY": "your_multilead_api_key_here"
      }
    }
  }
}
```

### 4. Restart Cursor

1. Reload window: `Cmd/Ctrl + R`
2. Or restart Cursor application

### 5. Verify Integration

In Cursor:

1. Open command palette: `Cmd/Ctrl + Shift + P`
2. Search for "MCP"
3. Check if Multilead server appears
4. Try using AI with "List my Multilead leads"

## Claude Code

Claude Code integrates MCP servers through `.claude/mcp.json`.

### 1. Create Configuration Directory

In your project root:

```bash
mkdir -p .claude
```

### 2. Create MCP Configuration

Create `.claude/mcp.json`:

```json
{
  "mcpServers": {
    "multilead": {
      "command": "python",
      "args": [
        "/absolute/path/to/multilead-mcp/server.py"
      ],
      "env": {
        "MULTILEAD_API_KEY": "your_multilead_api_key_here",
        "MULTILEAD_BASE_URL": "https://api.multilead.co",
        "TRANSPORT": "stdio",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### 3. Template Files

We provide template configuration files in `docs/setup/`:

```bash
# Copy template
cp docs/setup/claude-code-mcp.json .claude/mcp.json

# Edit configuration
nano .claude/mcp.json  # Replace path and API key
```

### 4. Restart Claude Code

1. Close all Claude Code windows
2. Reopen your project
3. Wait for server initialization

### 5. Verify Integration

In Claude Code:

1. Check server status in MCP panel
2. Ask: "What Multilead tools are available?"
3. Try: "Create a new lead for john@example.com"

## Configuration Templates

Pre-configured templates are available in `docs/setup/`:

- `claude-desktop-config.json` - Claude Desktop template
- `cursor-mcp-config.json` - Cursor template
- `claude-code-mcp.json` - Claude Code template
- `http-client-config.json` - HTTP client template

**Usage:**

```bash
# For Claude Desktop (macOS example)
cp docs/setup/claude-desktop-config.json ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Edit and add your API key
nano ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

## Advanced Configuration

### Multiple Environments

You can configure different environments in the same IDE:

```json
{
  "mcpServers": {
    "multilead-dev": {
      "command": "python",
      "args": ["/path/to/multilead-mcp/server.py"],
      "env": {
        "MULTILEAD_API_KEY": "dev_key_here"
      }
    },
    "multilead-prod": {
      "command": "python",
      "args": ["/path/to/multilead-mcp/server.py"],
      "env": {
        "MULTILEAD_API_KEY": "prod_key_here"
      }
    }
  }
}
```

### Using Virtual Environment

Specify the virtual environment Python:

```json
{
  "mcpServers": {
    "multilead": {
      "command": "/absolute/path/to/multilead-mcp/.venv/bin/python",
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

### Debug Logging

Enable debug logging for troubleshooting:

```json
{
  "mcpServers": {
    "multilead": {
      "command": "python",
      "args": ["/path/to/server.py"],
      "env": {
        "MULTILEAD_API_KEY": "your_api_key_here",
        "LOG_LEVEL": "DEBUG",
        "MULTILEAD_DEBUG": "true"
      }
    }
  }
}
```

## Troubleshooting

### Server Not Appearing

**Issue:** Multilead server doesn't appear in IDE

**Solutions:**

1. **Check configuration file location:**
   ```bash
   # macOS
   ls -la ~/Library/Application\ Support/Claude/claude_desktop_config.json
   
   # Linux
   ls -la ~/.config/Claude/claude_desktop_config.json
   ```

2. **Validate JSON syntax:**
   ```bash
   python -m json.tool < config.json
   ```

3. **Check IDE logs:**
   - Claude Desktop: Help → Show Logs
   - Cursor: View → Output → MCP
   - Claude Code: MCP panel → Logs

4. **Verify absolute paths:**
   ```bash
   python /absolute/path/to/multilead-mcp/server.py
   ```

5. **Restart IDE completely** (not just reload)

### Connection Errors

**Issue:** "Failed to connect to server"

**Solutions:**

1. **Check Python installation:**
   ```bash
   python --version  # Should be 3.10+
   ```

2. **Verify dependencies installed:**
   ```bash
   cd /path/to/multilead-mcp
   source .venv/bin/activate
   pip install -e .
   ```

3. **Test server manually:**
   ```bash
   cd /path/to/multilead-mcp
   python server.py
   ```

4. **Check API key:**
   - Verify key in configuration
   - Test at https://app.multilead.co/settings/api

### API Key Errors

**Issue:** "Authentication failed" or "API key not configured"

**Solutions:**

1. **Verify API key in config:**
   - No extra quotes
   - No spaces
   - Full key copied

2. **Check API key validity:**
   - Login to https://app.multilead.co/settings/api
   - Verify key is active
   - Regenerate if necessary

3. **Use environment file:**
   ```json
   {
     "mcpServers": {
       "multilead": {
         "command": "/path/to/multilead-mcp/start.sh"
       }
     }
   }
   ```

### Tools Not Available

**Issue:** Server connected but no tools visible

**Solutions:**

1. **Wait for initialization:** Server may take 5-10 seconds
2. **Check server logs:** Look for tool registration messages
3. **Restart IDE:** Complete restart, not just reload
4. **Verify server version:** Ensure latest version installed

### Performance Issues

**Issue:** Server slow or unresponsive

**Solutions:**

1. **Check timeout settings:**
   ```json
   "env": {
     "MULTILEAD_TIMEOUT": "60"
   }
   ```

2. **Enable debug logging:**
   ```json
   "env": {
     "LOG_LEVEL": "DEBUG"
   }
   ```

3. **Check network:** Verify internet connection and API access

4. **Monitor resources:**
   ```bash
   ps aux | grep python
   ```

### Windows-Specific Issues

**Issue:** Path issues on Windows

**Solutions:**

1. **Use forward slashes:**
   ```json
   "args": ["C:/Users/YourName/Projects/multilead-mcp/server.py"]
   ```

2. **Or escape backslashes:**
   ```json
   "args": ["C:\\Users\\YourName\\Projects\\multilead-mcp\\server.py"]
   ```

3. **Use WSL path (if using WSL):**
   ```json
   "args": ["/home/username/multilead-mcp/server.py"]
   ```

## Getting Help

If issues persist:

1. **Enable debug logging** and collect logs
2. **Test server manually** in terminal
3. **Check IDE documentation** for MCP support
4. **Review error messages** carefully
5. **Check GitHub issues** for similar problems

For Multilead API issues:
- Contact: https://app.multilead.co/support

For FastMCP framework issues:
- Documentation: https://gofastmcp.com

## Next Steps

- [Deployment Guide](../deployment/DEPLOYMENT.md)
- [Environment Variables Guide](ENVIRONMENT_VARIABLES.md)
- [Testing Guide](../testing/TESTING.md)
