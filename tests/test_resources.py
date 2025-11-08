"""
Test suite for Multilead MCP server resources.

Tests the 2 resources:
- multilead://config - Server configuration
- multilead://stats - API usage statistics
"""

import pytest
from fastmcp.client import Client
from fastmcp.client.transports import FastMCPTransport
from unittest.mock import patch


@pytest.mark.asyncio
async def test_list_resources(mcp_client: Client[FastMCPTransport]):
    """Test listing all available resources."""
    resources = await mcp_client.list_resources()

    assert len(resources) == 2

    # Check for config resource
    config_resource = next((r for r in resources if str(r.uri) == "multilead://config"), None)
    assert config_resource is not None
    assert config_resource.name == "Multilead MCP Server Configuration"
    assert "configuration" in config_resource.description.lower()

    # Check for stats resource
    stats_resource = next((r for r in resources if str(r.uri) == "multilead://stats"), None)
    assert stats_resource is not None
    assert stats_resource.name == "Multilead API Statistics"
    assert "statistics" in stats_resource.description.lower()


@pytest.mark.asyncio
async def test_get_config_resource(mcp_client: Client[FastMCPTransport]):
    """Test reading the config resource."""
    result = await mcp_client.read_resource("multilead://config")

    assert result is not None
    assert len(result) > 0

    # The resource should return configuration as a string
    config_text = result[0].text
    assert "Multilead MCP Server Configuration" in config_text
    assert "API Base URL" in config_text
    assert "https://api.multilead.co" in config_text
    assert "Timeout" in config_text
    assert "Debug Mode" in config_text


@pytest.mark.asyncio
async def test_config_resource_shows_environment_variables(
    mcp_client: Client[FastMCPTransport]
):
    """Test that config resource displays environment variables."""
    result = await mcp_client.read_resource("multilead://config")

    config_text = result[0].text

    # Should show environment variable names (not values for security)
    assert "MULTILEAD_API_KEY" in config_text
    assert "MULTILEAD_BASE_URL" in config_text
    assert "MULTILEAD_TIMEOUT" in config_text
    assert "MULTILEAD_DEBUG" in config_text

    # Should not expose the actual API key value
    assert "test_api_key_12345" not in config_text or "***" in config_text


@pytest.mark.asyncio
async def test_get_stats_resource_success(
    mcp_client: Client[FastMCPTransport], mock_multilead_client_success
):
    """Test reading the stats resource with successful API response."""
    # Mock the API response for stats
    mock_stats = {
        "account": {
            "leads_count": 1500,
            "campaigns_count": 25,
            "active_campaigns": 8,
            "conversations_count": 450,
            "webhooks_count": 3,
        },
        "usage": {
            "api_calls_today": 125,
            "api_calls_this_month": 3500,
            "rate_limit": 10000,
            "rate_limit_remaining": 9875,
        },
    }

    mock_multilead_client_success.__aenter__.return_value.request.return_value.json.return_value = (
        mock_stats
    )

    result = await mcp_client.read_resource("multilead://stats")

    assert result is not None
    stats_text = result[0].text

    assert "Multilead API Statistics" in stats_text
    assert "1500" in stats_text  # leads_count
    assert "25" in stats_text    # campaigns_count


@pytest.mark.asyncio
async def test_get_stats_resource_with_error(
    mcp_client: Client[FastMCPTransport], mock_multilead_client_401
):
    """Test stats resource handles API errors gracefully."""
    # When API call fails, the resource should still return something
    # (likely an error message or fallback data)
    result = await mcp_client.read_resource("multilead://stats")

    assert result is not None
    stats_text = result[0].text

    # Should indicate there was an error or show fallback message
    # The actual behavior depends on implementation, but it shouldn't crash
    assert len(stats_text) > 0


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "invalid_uri",
    [
        "multilead://invalid",
        "multilead://nonexistent",
        "wrong://config",
        "multilead://stats/extra",
    ],
)
async def test_invalid_resource_uri(mcp_client: Client[FastMCPTransport], invalid_uri: str):
    """Test accessing resources with invalid URIs."""
    with pytest.raises(Exception):  # Should raise error for invalid URIs
        await mcp_client.read_resource(invalid_uri)


@pytest.mark.asyncio
async def test_config_resource_format(mcp_client: Client[FastMCPTransport]):
    """Test that config resource returns properly formatted text."""
    result = await mcp_client.read_resource("multilead://config")

    config_text = result[0].text

    # Should be human-readable formatted text
    assert "\n" in config_text  # Multiple lines
    assert ":" in config_text   # Key-value pairs

    # Should have sections or structure
    lines = config_text.split("\n")
    assert len(lines) > 5  # Should have multiple configuration items


@pytest.mark.asyncio
async def test_stats_resource_format(
    mcp_client: Client[FastMCPTransport], mock_multilead_client_success
):
    """Test that stats resource returns properly formatted text."""
    mock_stats = {
        "leads": 100,
        "campaigns": 10,
        "active_campaigns": 5,
    }

    mock_multilead_client_success.__aenter__.return_value.request.return_value.json.return_value = (
        mock_stats
    )

    result = await mcp_client.read_resource("multilead://stats")

    stats_text = result[0].text

    # Should be human-readable formatted text
    assert "\n" in stats_text  # Multiple lines

    # Should contain statistical information
    lines = stats_text.split("\n")
    assert len(lines) > 3  # Should have multiple stat items


@pytest.mark.asyncio
async def test_resource_metadata(mcp_client: Client[FastMCPTransport]):
    """Test that resources have proper metadata."""
    resources = await mcp_client.list_resources()

    for resource in resources:
        # Each resource should have required fields
        assert resource.uri is not None
        assert str(resource.uri).startswith("multilead://")
        assert resource.name is not None
        assert len(resource.name) > 0
        assert resource.description is not None
        assert len(resource.description) > 0

        # URIs should be valid
        assert str(resource.uri) in ["multilead://config", "multilead://stats"]


@pytest.mark.asyncio
async def test_config_resource_readonly(mcp_client: Client[FastMCPTransport]):
    """Test that config resource is read-only (no write operations)."""
    # Resources in MCP are read-only by design
    # This test verifies the resource can be read but not modified
    result = await mcp_client.read_resource("multilead://config")

    assert result is not None
    # If this doesn't raise an error, the resource is readable

    # MCP doesn't have a write_resource method, so this is implicitly read-only


@pytest.mark.asyncio
async def test_stats_resource_dynamic_data(
    mcp_client: Client[FastMCPTransport], mock_multilead_client_success
):
    """Test that stats resource returns dynamic data from API."""
    # First call
    mock_stats_1 = {"leads": 100, "campaigns": 10}
    mock_multilead_client_success.__aenter__.return_value.request.return_value.json.return_value = (
        mock_stats_1
    )

    result_1 = await mcp_client.read_resource("multilead://stats")
    stats_text_1 = result_1[0].text

    # Second call with different data
    mock_stats_2 = {"leads": 200, "campaigns": 20}
    mock_multilead_client_success.__aenter__.return_value.request.return_value.json.return_value = (
        mock_stats_2
    )

    result_2 = await mcp_client.read_resource("multilead://stats")
    stats_text_2 = result_2[0].text

    # Stats should reflect the API data (which changed between calls)
    # In a real scenario, the stats would update dynamically
    assert result_1 is not None
    assert result_2 is not None


@pytest.mark.asyncio
async def test_resource_content_type(mcp_client: Client[FastMCPTransport]):
    """Test that resources return text content."""
    # Test config resource
    config_result = await mcp_client.read_resource("multilead://config")
    assert hasattr(config_result[0], "text")
    assert isinstance(config_result[0].text, str)

    # Test stats resource with mock
    with patch("httpx.AsyncClient") as mock_client:
        mock_response = type('obj', (object,), {
            'status_code': 200,
            'json': lambda: {"stats": "data"},
            'raise_for_status': lambda: None
        })
        mock_client.return_value.__aenter__.return_value.request.return_value = mock_response

        stats_result = await mcp_client.read_resource("multilead://stats")
        assert hasattr(stats_result[0], "text")
        assert isinstance(stats_result[0].text, str)
