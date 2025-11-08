# Multilead MCP Server - Testing Guide

Comprehensive testing documentation for the Multilead MCP server.

## Table of Contents

- [Overview](#overview)
- [Test Suite Structure](#test-suite-structure)
- [Setup](#setup)
- [Running Tests](#running-tests)
- [Test Coverage](#test-coverage)
- [Test Categories](#test-categories)
- [Writing New Tests](#writing-new-tests)
- [Troubleshooting](#troubleshooting)

## Overview

The Multilead MCP server test suite uses **pytest** with the **FastMCP in-memory testing pattern** to test all 77 tools, 2 resources, and 2 prompts without requiring an actual HTTP server or real API calls.

### Testing Pattern

We follow the recommended FastMCP testing pattern from [gofastmcp.com/patterns/testing](https://gofastmcp.com/patterns/testing):

```python
# In-memory testing - no HTTP server needed
async with Client(transport=mcp) as client:
    result = await client.call_tool("tool_name", {...})
```

### Key Features

- **In-memory testing**: No HTTP server required
- **Mocked API calls**: All Multilead API requests are mocked
- **Comprehensive coverage**: Tests for all 77 tools, 2 resources, 2 prompts
- **Error scenario testing**: Tests for 401, 404, 429, 500 errors and timeouts
- **Parametrized tests**: Multiple test cases with different inputs
- **Async support**: Full async/await testing with pytest-asyncio

## Test Suite Structure

```
multilead-mcp/
├── tests/
│   ├── __init__.py              # (optional) Package marker
│   ├── conftest.py              # Shared fixtures and configuration
│   ├── test_tools.py            # Tests for all 77 tools
│   ├── test_resources.py        # Tests for 2 resources
│   ├── test_prompts.py          # Tests for 2 prompts
│   └── pytest.ini               # Pytest configuration
├── pyproject.toml               # Dependencies and project config
└── TESTING.md                   # This file
```

### Test Files

| File | Purpose | Tests Count |
|------|---------|-------------|
| `conftest.py` | Shared fixtures (mcp_client, mock responses) | - |
| `test_tools.py` | All 77 MCP tools | ~50+ tests |
| `test_resources.py` | Config and stats resources | ~15 tests |
| `test_prompts.py` | Lead enrichment and campaign analysis prompts | ~20 tests |

## Setup

### 1. Install Dependencies

Using pip with the dev extras:

```bash
cd /home/gotime2022/Projects/mcp-servers/multilead-mcp

# Install with dev dependencies
pip install -e ".[dev]"
```

Or install test dependencies directly:

```bash
pip install pytest>=8.0.0 \
            pytest-asyncio>=0.23.0 \
            pytest-cov>=4.0.0 \
            pytest-mock>=3.12.0 \
            inline-snapshot>=0.13.0 \
            dirty-equals>=0.7.0
```

### 2. Set Environment Variables

The tests use mock environment variables automatically via the `set_test_env_vars` fixture in `conftest.py`:

```python
# Set automatically in conftest.py
MULTILEAD_API_KEY=test_api_key_12345
MULTILEAD_BASE_URL=https://api.multilead.co
MULTILEAD_TIMEOUT=30
MULTILEAD_DEBUG=false
```

**Note**: No real API key is needed for testing since all API calls are mocked.

## Running Tests

### Run All Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=. --cov-report=html --cov-report=term
```

### Run Specific Test Files

```bash
# Test only tools
pytest tests/test_tools.py

# Test only resources
pytest tests/test_resources.py

# Test only prompts
pytest tests/test_prompts.py
```

### Run Specific Tests

```bash
# Run a specific test by name
pytest tests/test_tools.py::test_create_lead_success

# Run tests matching a pattern
pytest -k "lead"           # All tests with "lead" in name
pytest -k "error"          # All error handling tests
pytest -k "create or delete"  # Tests with "create" OR "delete"
```

### Run with Markers

```bash
# Run only async tests
pytest -m asyncio

# Run only error handling tests
pytest -m error_handling

# Run all except slow tests
pytest -m "not slow"
```

### Parallel Test Execution

```bash
# Install pytest-xdist
pip install pytest-xdist

# Run tests in parallel (4 workers)
pytest -n 4
```

## Test Coverage

### Generate Coverage Report

```bash
# Generate HTML and terminal coverage report
pytest --cov=. --cov-report=html --cov-report=term

# Open HTML report
# HTML report will be in htmlcov/index.html
```

### Coverage Goals

- **Overall coverage**: Target 80%+ for production readiness
- **Tool coverage**: All 77 tools should have at least 2 tests (success + error)
- **Resource coverage**: Both resources tested for valid and invalid scenarios
- **Prompt coverage**: Both prompts tested for content and format

### Current Coverage Areas

| Component | Coverage | Notes |
|-----------|----------|-------|
| Tools (77) | ~50+ tests | Success cases, error handling, parametrized tests |
| Resources (2) | ~15 tests | Config, stats, format validation |
| Prompts (2) | ~20 tests | Content, structure, metadata validation |
| Error Handling | ~10 tests | 401, 404, 429, 500, timeout scenarios |

## Test Categories

### 1. Tool Tests (`test_tools.py`)

Tests all 77 tools across categories:

#### Lead Management (32 tools)
- `test_create_lead_success` - Create lead with valid data
- `test_create_lead_parametrized` - Multiple parameter sets
- `test_get_lead_success` - Retrieve lead by ID
- `test_get_lead_not_found` - Handle 404 error
- `test_list_leads_success` - List with filters
- `test_update_lead_success` - Update lead data
- `test_delete_lead_success` - Delete lead
- `test_add_leads_to_campaign_success` - Add leads to campaign
- `test_pause_lead_execution` - Pause lead in campaign
- `test_resume_lead_execution` - Resume lead execution
- `test_assign_tag_to_lead` - Tag management
- `test_remove_tag_from_lead` - Remove tags

#### Campaign Management (12 tools)
- `test_get_campaign_info` - Retrieve campaign details
- `test_get_campaign_list` - List all campaigns
- `test_create_campaign_from_template` - Create from template
- `test_export_all_campaigns` - Export campaigns
- `test_get_leads_from_campaign` - Get campaign leads

#### Statistics (7 tools)
- `test_get_statistics` - Campaign statistics
- `test_export_statistics_csv` - Export stats as CSV
- `test_get_all_campaigns_statistics` - Overall stats

#### Conversations (15 tools)
- `test_get_messages_from_specific_thread` - Thread messages
- `test_get_all_conversations` - All conversations
- `test_get_unread_conversations` - Unread messages
- `test_mark_messages_as_seen` - Mark as read
- `test_send_new_email` - Send email
- `test_send_email_reply` - Reply to email
- `test_send_linkedin_message` - LinkedIn messaging

#### Webhooks (8 tools)
- `test_create_webhook` - Create webhook
- `test_list_webhooks` - List webhooks
- `test_delete_webhook` - Delete webhook
- `test_create_global_webhook` - Global webhook

#### User Management (10 tools)
- `test_get_user_information` - User info
- `test_register_new_user` - User registration
- `test_list_all_seats_of_specific_user` - User seats
- `test_create_seat` - Create seat
- `test_send_password_reset_email` - Password reset

#### Team Management (5 tools)
- `test_create_team` - Create team
- `test_get_team_members` - Team members
- `test_invite_team_member` - Invite member

#### Error Handling
- `test_unauthorized_request` - 401 errors
- `test_rate_limit_error` - 429 rate limits
- `test_server_error` - 500 server errors
- `test_timeout_error` - Request timeouts

#### Settings (3 tools)
- `test_add_keywords_to_global_blacklist` - Blacklist keywords
- `test_activate_inboxflare_warmup` - Email warmup
- `test_connect_linkedin_account` - LinkedIn integration
- `test_disconnect_linkedin_account` - Disconnect LinkedIn

### 2. Resource Tests (`test_resources.py`)

Tests for the 2 MCP resources:

- `test_list_resources` - List all resources
- `test_get_config_resource` - Config resource content
- `test_config_resource_shows_environment_variables` - Env var display
- `test_get_stats_resource_success` - Stats with API response
- `test_get_stats_resource_with_error` - Stats error handling
- `test_invalid_resource_uri` - Invalid URI handling
- `test_config_resource_format` - Format validation
- `test_stats_resource_format` - Stats format
- `test_resource_metadata` - Metadata validation

### 3. Prompt Tests (`test_prompts.py`)

Tests for the 2 MCP prompts:

- `test_list_prompts` - List all prompts
- `test_get_lead_enrichment_prompt` - Lead enrichment content
- `test_lead_enrichment_prompt_content_structure` - Structure validation
- `test_get_campaign_analysis_prompt` - Campaign analysis content
- `test_campaign_analysis_prompt_content_structure` - Structure validation
- `test_prompt_without_arguments` - No arguments needed
- `test_invalid_prompt_name` - Invalid prompt handling
- `test_prompt_metadata` - Metadata validation
- `test_prompts_are_distinct` - Content uniqueness
- `test_prompt_consistency_across_calls` - Consistency check

## Writing New Tests

### Test Template for Tools

```python
@pytest.mark.asyncio
async def test_new_tool_success(
    mcp_client: Client[FastMCPTransport],
    mock_multilead_client_success
):
    """Test description."""
    # Setup mock response
    mock_response = {"result": "success"}
    mock_multilead_client_success.__aenter__.return_value.request.return_value.json.return_value = mock_response

    # Call the tool
    result = await mcp_client.call_tool(
        "tool_name",
        {"param1": "value1", "param2": "value2"}
    )

    # Assert results
    assert result.data["result"] == "success"
```

### Parametrized Test Template

```python
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "param1,param2,expected",
    [
        ("value1", "value2", "result1"),
        ("value3", "value4", "result2"),
        ("value5", "value6", "result3"),
    ],
)
async def test_parametrized_tool(
    mcp_client: Client[FastMCPTransport],
    mock_multilead_client_success,
    param1: str,
    param2: str,
    expected: str,
):
    """Test with multiple parameter sets."""
    mock_response = {"result": expected}
    mock_multilead_client_success.__aenter__.return_value.request.return_value.json.return_value = mock_response

    result = await mcp_client.call_tool(
        "tool_name",
        {"param1": param1, "param2": param2}
    )

    assert result.data["result"] == expected
```

### Error Handling Test Template

```python
@pytest.mark.asyncio
async def test_tool_error_handling(
    mcp_client: Client[FastMCPTransport],
    mock_multilead_client_404  # or 401, 429, 500, timeout
):
    """Test error scenario."""
    with pytest.raises(Exception):  # ToolError wrapped in Exception
        await mcp_client.call_tool("tool_name", {"param": "value"})
```

## Troubleshooting

### Common Issues

#### 1. Import Errors

**Problem**: `ModuleNotFoundError: No module named 'server'`

**Solution**:
```bash
# Ensure you're in the right directory
cd /home/gotime2022/Projects/mcp-servers/multilead-mcp

# Install package in development mode
pip install -e .
```

#### 2. Async Test Warnings

**Problem**: `RuntimeWarning: coroutine was never awaited`

**Solution**: Ensure test functions are marked with `@pytest.mark.asyncio`:
```python
@pytest.mark.asyncio
async def test_my_async_function():
    result = await some_async_function()
```

#### 3. Mock Not Working

**Problem**: Real API calls being made instead of mocked calls

**Solution**: Check that you're using the fixture correctly:
```python
async def test_tool(
    mcp_client: Client[FastMCPTransport],
    mock_multilead_client_success  # ← Include this fixture
):
    # Configure mock before calling tool
    mock_multilead_client_success.__aenter__.return_value.request.return_value.json.return_value = {"data": "value"}
```

#### 4. Environment Variable Issues

**Problem**: `ValueError: MULTILEAD_API_KEY environment variable is required`

**Solution**: The `set_test_env_vars` fixture should handle this automatically. If not, check:
```bash
# Verify conftest.py is being loaded
pytest --fixtures | grep set_test_env_vars
```

#### 5. Coverage Not Working

**Problem**: Coverage report shows 0% coverage

**Solution**:
```bash
# Install coverage dependencies
pip install pytest-cov

# Run with correct source path
pytest --cov=. --cov-report=term

# Or specify the module
pytest --cov=server --cov-report=term
```

### Debug Mode

Run tests with verbose output and show print statements:

```bash
# Maximum verbosity
pytest -vv -s

# Show local variables on failure
pytest -l

# Drop into debugger on failure
pytest --pdb

# Stop after first failure
pytest -x
```

### Collecting Tests

See which tests will run without executing them:

```bash
# Collect all tests
pytest --collect-only

# Collect specific file
pytest tests/test_tools.py --collect-only

# Count tests
pytest --collect-only -q
```

## Best Practices

### 1. Test Naming
- Use descriptive names: `test_create_lead_success` not `test_cl`
- Include scenario: `test_get_lead_not_found` vs `test_get_lead_success`
- Use underscores: `test_my_function` not `testMyFunction`

### 2. Fixtures
- Use shared fixtures from `conftest.py`
- Create new fixtures for complex setup
- Keep fixtures focused and single-purpose

### 3. Assertions
- Use specific assertions: `assert result.data["id"] == "lead_123"`
- Add messages for clarity: `assert len(leads) > 0, "Should return at least one lead"`
- Test both positive and negative cases

### 4. Mocking
- Mock at the HTTP client level (httpx.AsyncClient)
- Use fixtures for common mock scenarios
- Configure mocks before calling the tool

### 5. Test Organization
- Group related tests together
- Use descriptive comments for sections
- Keep tests independent (no shared state)

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install -e ".[dev]"
      - name: Run tests
        run: |
          pytest --cov=. --cov-report=xml --cov-report=term
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

## Resources

- **FastMCP Testing Docs**: https://gofastmcp.com/patterns/testing
- **Pytest Documentation**: https://docs.pytest.org/
- **pytest-asyncio**: https://pytest-asyncio.readthedocs.io/
- **Multilead API Docs**: https://docs.multilead.co/api-reference

## Support

For issues or questions about testing:

1. Check this documentation first
2. Review the test examples in the test files
3. Consult FastMCP testing documentation
4. Check pytest documentation for specific pytest features

---

**Last Updated**: 2025-11-05
**Test Suite Version**: 1.0.0
**Total Tests**: ~85+ tests across all categories
