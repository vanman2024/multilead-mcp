# Multilead Open API MCP Server

A comprehensive FastMCP server providing access to the **Multilead Open API** with 74 endpoints for lead management, campaigns, conversations, webhooks, and analytics.

<a href="https://glama.ai/mcp/servers/@vanman2024/multilead-mcp">
  <img width="380" height="200" src="https://glama.ai/mcp/servers/@vanman2024/multilead-mcp/badge" alt="Multilead Open API Server MCP server" />
</a>

## Overview

This MCP server enables Claude and other AI assistants to interact with the Multilead platform for:

- **Lead Management (32 endpoints)**: Create, retrieve, update, delete, search, and enrich leads with custom fields and tags
- **Campaign Management (12 endpoints)**: Design, execute, and monitor email campaigns with advanced targeting
- **Conversations (15 endpoints)**: Access email threads, message history, and conversation analytics
- **Webhooks (8 endpoints)**: Set up real-time event notifications for leads, campaigns, and conversations
- **Analytics & Reporting (7 endpoints)**: Generate performance reports, track metrics, and analyze trends

## Features

- Full async/await support for high-performance operations
- Comprehensive error handling with helpful error messages
- Authentication via Bearer token (API key)
- Rate limiting and retry logic
- Type-safe operations using Pydantic models
- Example tools, resources, and prompts included
- Production-ready structure for adding all 74 API endpoints

## Prerequisites

- **Python 3.10 or higher**
- **Package manager**: `uv` (recommended) or `pip`
- **Multilead API Key**: Get yours at [https://app.multilead.co/settings/api](https://app.multilead.co/settings/api)

## Installation

### 1. Clone or Navigate to Project

```bash
cd /home/gotime2022/Projects/mcp-servers/multilead-mcp
```

### 2. Create Virtual Environment

**Using uv (recommended):**

```bash
uv venv
source .venv/bin/activate  # On Linux/Mac
# or
.venv\Scripts\activate  # On Windows
```

**Using standard venv:**

```bash
python -m venv .venv
source .venv/bin/activate  # On Linux/Mac
# or
.venv\Scripts\activate  # On Windows
```

### 3. Install Dependencies

**Using uv:**

```bash
uv pip install -e .
```

**Using pip:**

```bash
pip install -e .
```

### 4. Configure Environment Variables

Copy the example environment file and add your API key:

```bash
cp .env.example .env
```

Edit `.env` and replace `your_multilead_api_key_here` with your actual API key:

```env
MULTILEAD_API_KEY=ml_live_abc123xyz...
MULTILEAD_BASE_URL=https://api.multilead.co
MULTILEAD_TIMEOUT=30
MULTILEAD_DEBUG=false
```

**Important**: Never commit your `.env` file to version control. It's already in `.gitignore`.

## Usage

### Quick Start

#### STDIO Mode (For Claude Desktop/Code/Cursor)

```bash
# 1. Configure environment
cp .env.example .env
nano .env  # Add your MULTILEAD_API_KEY

# 2. Start server
./start.sh
```

#### HTTP Mode (For Remote Access)

```bash
# 1. Configure environment
cp .env.example .env
nano .env  # Add your MULTILEAD_API_KEY

# 2. Start HTTP server
./start-http.sh
```

The server will be available at:
- MCP Endpoint: `http://localhost:8000/mcp`
- Health Check: `http://localhost:8000/health`

### Advanced Usage

#### Custom HTTP Configuration

```bash
# Custom host and port
./start-http.sh --host 127.0.0.1 --port 3000

# Production mode (JSON logs)
./start-http.sh --production

# Debug mode
./start-http.sh --log-level DEBUG
```

#### Manual Startup

**STDIO:**
```bash
source .venv/bin/activate
export TRANSPORT=stdio
python server.py
```

**HTTP:**
```bash
source .venv/bin/activate
export TRANSPORT=http
export PORT=8000
python server.py
```

### Health Check

When running in HTTP mode, check server health:

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "multilead-mcp",
  "version": "1.0.0",
  "transport": "http",
  "api_configured": true
}
```

## Deployment

The Multilead MCP Server supports two deployment modes:

### STDIO Deployment (Local/IDE Integration)

For Claude Desktop, Cursor, and Claude Code integration.

**Quick Setup:**

1. Copy IDE configuration template:
   ```bash
   # For Claude Desktop (macOS)
   cp docs/setup/claude-desktop-config.json ~/Library/Application\ Support/Claude/claude_desktop_config.json

   # For Cursor
   cp docs/setup/cursor-mcp-config.json .cursor/mcp_config.json

   # For Claude Code
   cp docs/setup/claude-code-mcp.json .claude/mcp.json
   ```

2. Edit configuration file and add your API key

3. Restart your IDE

**Detailed Guide:** [IDE Setup Guide](docs/setup/IDE_SETUP.md)

### HTTP Deployment (Remote Access)

For web services, remote access, and cloud deployment.

**Development:**
```bash
./start-http.sh
```

**Production:**
See the complete [Deployment Guide](docs/deployment/DEPLOYMENT.md) for:
- systemd service configuration
- Docker deployment
- nginx reverse proxy setup
- SSL/TLS configuration
- Production best practices

### Production Features

The server includes production-ready middleware:

- **Structured Logging**: JSON or text format, file rotation
- **Request Logging**: All requests logged with timing
- **Error Handling**: Graceful error responses with proper status codes
- **Rate Limiting**: Configurable per-minute and per-hour limits (100/min, 1000/hr default)
- **Health Checks**: `/health` endpoint for monitoring
- **Response Timing**: `X-Response-Time` header on all responses

**Configuration:**
```env
LOG_LEVEL=INFO              # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT=json             # json (production) or text (development)
RATE_LIMIT_PER_MINUTE=100   # Requests per minute
RATE_LIMIT_PER_HOUR=1000    # Requests per hour
```

### Documentation

Complete deployment documentation is available in the `docs/` directory:

- **[Deployment Guide](docs/deployment/DEPLOYMENT.md)** - Complete deployment instructions
- **[Deployment Checklist](docs/deployment/DEPLOYMENT_CHECKLIST.md)** - Pre/post deployment checklist
- **[IDE Setup Guide](docs/setup/IDE_SETUP.md)** - Claude Desktop, Cursor, Claude Code integration
- **[Environment Variables](docs/setup/ENVIRONMENT_VARIABLES.md)** - Complete variable reference
- **Configuration Templates** in `docs/setup/` - Ready-to-use IDE configs

## Available Tools

### Lead Management (5 tools implemented)

1. **create_lead**: Create a new lead with email, name, company, tags, and custom fields
2. **get_lead**: Retrieve a lead by ID with all properties
3. **list_leads**: List and filter leads with pagination and filtering
4. **update_lead**: Update lead properties, tags, and custom fields
5. **delete_lead**: Delete a lead by ID

**Example usage with Claude:**

```
Create a new lead with email "john@example.com", first name "John",
last name "Doe", company "Acme Corp", and tags ["enterprise", "qualified"]
```

### Resources

1. **multilead://config**: Server configuration and API status
2. **multilead://stats**: API usage statistics and account information

### Prompts

1. **lead_enrichment_prompt**: Template for enriching lead data with AI analysis
2. **campaign_analysis_prompt**: Template for analyzing campaign performance

## API Coverage

### Current Implementation

- 5 core lead management tools (create, read, update, delete, list)
- 2 informational resources
- 2 AI prompt templates
- Full error handling and authentication

### Planned Tools (69 endpoints remaining)

**Lead Management (27 more)**:
- Bulk import/export
- Lead scoring and enrichment
- Tag management
- Custom field operations
- Lead lifecycle tracking
- Duplicate detection
- Lead assignment

**Campaign Management (12 endpoints)**:
- Campaign CRUD operations
- Template management
- Segment targeting
- Schedule management
- Performance tracking
- A/B testing

**Conversations (15 endpoints)**:
- Thread retrieval
- Message history
- Participant tracking
- Conversation analytics
- Export capabilities

**Webhooks (8 endpoints)**:
- Webhook registration
- Event subscriptions
- Delivery logs
- Webhook testing

**Analytics (7 endpoints)**:
- Lead reports
- Campaign analytics
- Engagement metrics
- Custom reporting

## Project Structure

```
multilead-mcp/
├── server.py                          # Main FastMCP server implementation
├── pyproject.toml                     # Project metadata and dependencies
├── .env.example                       # Environment variable template
├── .gitignore                        # Git ignore patterns
├── README.md                         # This file
├── start.sh                          # STDIO startup script
├── start-http.sh                     # HTTP startup script
├── docs/                             # Complete documentation
│   ├── deployment/                   # Deployment guides
│   │   ├── DEPLOYMENT.md            # Complete deployment guide
│   │   ├── DEPLOYMENT_CHECKLIST.md  # Deployment checklist
│   │   └── .env.production          # Production environment template
│   ├── setup/                        # Setup and configuration
│   │   ├── IDE_SETUP.md             # IDE integration guide
│   │   ├── ENVIRONMENT_VARIABLES.md # Environment variables reference
│   │   ├── claude-desktop-config.json  # Claude Desktop template
│   │   ├── cursor-mcp-config.json      # Cursor template
│   │   ├── claude-code-mcp.json        # Claude Code template
│   │   └── http-client-config.json     # HTTP client template
│   └── testing/                      # Testing documentation
├── logs/                             # Server logs (HTTP mode only, gitignored)
└── tests/                            # Test suite (to be implemented)
    └── test_server.py
```

## Development

### Adding New Tools

Follow the pattern in `server.py`:

```python
@mcp.tool()
async def your_new_tool(
    param1: str,
    param2: Optional[int] = None
) -> Dict[str, Any]:
    """
    Tool description for LLM

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Response data from API
    """
    result = await client.request(
        "GET",
        "/v1/your-endpoint",
        params={"param1": param1, "param2": param2}
    )
    return result
```

### Code Quality

```bash
# Format code
black server.py

# Lint code
ruff check server.py

# Type checking (optional)
mypy server.py
```

## Security Best Practices

- **Never hardcode API keys** in source code
- Always use environment variables for secrets
- The `.env` file is in `.gitignore` to prevent accidental commits
- API keys are never logged or exposed in error messages
- Use `.env.example` as a template with placeholders only

## Troubleshooting

### Authentication Errors

```
Error: Authentication failed. Please check your MULTILEAD_API_KEY.
```

**Solution**: Verify your API key is correct and active at [https://app.multilead.co/settings/api](https://app.multilead.co/settings/api)

### Timeout Errors

```
Error: Request timed out after 30 seconds.
```

**Solution**: Increase the timeout in your `.env` file:

```env
MULTILEAD_TIMEOUT=60
```

### Rate Limiting

```
Error: Rate limit exceeded. Please wait before making more requests.
```

**Solution**: The API has rate limits. Wait a few minutes before retrying. Consider implementing request queuing for high-volume operations.

### Connection Errors

```
Error: Network error while connecting to Multilead API
```

**Solution**:
1. Check your internet connection
2. Verify the `MULTILEAD_BASE_URL` is correct
3. Check if Multilead API is operational

## API Documentation

For complete API reference, visit:
- **Official Docs**: [https://docs.multilead.co/api-reference](https://docs.multilead.co/api-reference)
- **API Dashboard**: [https://app.multilead.co/settings/api](https://app.multilead.co/settings/api)

## FastMCP Documentation

Learn more about FastMCP:
- **Getting Started**: [https://gofastmcp.com/getting-started/welcome](https://gofastmcp.com/getting-started/welcome)
- **Server Guide**: [https://gofastmcp.com/servers/server](https://gofastmcp.com/servers/server)
- **Tools**: [https://gofastmcp.com/servers/tools](https://gofastmcp.com/servers/tools)

## Contributing

Contributions are welcome! To add more endpoints:

1. Review the Multilead API documentation
2. Add the tool function following existing patterns
3. Include proper type hints and docstrings
4. Test the endpoint manually
5. Update this README with the new tool

## License

MIT License - See LICENSE file for details

## Support

For issues with:
- **This MCP server**: Open an issue in the repository
- **Multilead API**: Contact [Multilead support](https://app.multilead.co/support)
- **FastMCP framework**: Visit [FastMCP documentation](https://gofastmcp.com)

## Changelog

### Version 1.0.0 (2025-11-05)

- Initial release
- 5 core lead management tools implemented
- 2 informational resources
- 2 AI prompt templates
- Full authentication and error handling
- Production-ready foundation for 74 API endpoints