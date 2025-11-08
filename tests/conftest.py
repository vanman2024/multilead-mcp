"""
Shared pytest fixtures for Multilead MCP server testing.

This module provides fixtures for in-memory testing of the FastMCP server
using the recommended testing pattern from https://gofastmcp.com/patterns/testing
"""

import os
from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from fastmcp.client import Client
from fastmcp.client.transports import FastMCPTransport


@pytest.fixture(scope="session", autouse=True)
def set_test_env_vars():
    """Set required environment variables for testing."""
    os.environ["MULTILEAD_API_KEY"] = "test_api_key_12345"
    os.environ["MULTILEAD_BASE_URL"] = "https://api.multilead.co"
    os.environ["MULTILEAD_TIMEOUT"] = "30"
    os.environ["MULTILEAD_DEBUG"] = "false"


@pytest.fixture
async def mcp_client() -> AsyncGenerator[Client[FastMCPTransport], None]:
    """
    Create in-memory MCP client for testing.

    This fixture uses the FastMCP in-memory testing pattern to avoid
    starting an actual HTTP server during tests.

    Yields:
        Client instance connected to the MCP server
    """
    # Import server to get the mcp instance
    from server import mcp

    async with Client(transport=mcp) as client:
        yield client


@pytest.fixture
def mock_httpx_client():
    """
    Mock httpx.AsyncClient for testing HTTP requests.

    Returns:
        MagicMock configured to simulate httpx responses
    """
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"success": True, "data": {}}
    mock_response.raise_for_status = MagicMock()

    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None
    mock_client.request = AsyncMock(return_value=mock_response)

    return mock_client


@pytest.fixture
def mock_multilead_client_success(mock_httpx_client: MagicMock):
    """
    Mock MultileadClient with successful responses.

    Patches httpx.AsyncClient to return successful mock responses.
    """
    with patch("httpx.AsyncClient", return_value=mock_httpx_client):
        yield mock_httpx_client


@pytest.fixture
def mock_multilead_client_401():
    """Mock MultileadClient returning 401 Unauthorized."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.raise_for_status = MagicMock()

    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None
    mock_client.request = AsyncMock(return_value=mock_response)

    with patch("httpx.AsyncClient", return_value=mock_client):
        yield mock_client


@pytest.fixture
def mock_multilead_client_404():
    """Mock MultileadClient returning 404 Not Found."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.raise_for_status = MagicMock()

    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None
    mock_client.request = AsyncMock(return_value=mock_response)

    with patch("httpx.AsyncClient", return_value=mock_client):
        yield mock_client


@pytest.fixture
def mock_multilead_client_429():
    """Mock MultileadClient returning 429 Rate Limit."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.status_code = 429
    mock_response.raise_for_status = MagicMock()

    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None
    mock_client.request = AsyncMock(return_value=mock_response)

    with patch("httpx.AsyncClient", return_value=mock_client):
        yield mock_client


@pytest.fixture
def mock_multilead_client_500():
    """Mock MultileadClient returning 500 Server Error."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.raise_for_status = MagicMock()

    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None
    mock_client.request = AsyncMock(return_value=mock_response)

    with patch("httpx.AsyncClient", return_value=mock_client):
        yield mock_client


@pytest.fixture
def mock_multilead_client_timeout():
    """Mock MultileadClient raising TimeoutException."""
    mock_client = MagicMock()
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None
    mock_client.request = AsyncMock(side_effect=httpx.TimeoutException("Request timeout"))

    with patch("httpx.AsyncClient", return_value=mock_client):
        yield mock_client


@pytest.fixture
def mock_lead_response():
    """Sample lead response data."""
    return {
        "id": "lead_123",
        "email": "test@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "company": "Test Corp",
        "position": "CEO",
        "tags": ["prospect", "high-value"],
        "created_at": "2025-11-05T12:00:00Z",
        "updated_at": "2025-11-05T12:00:00Z",
    }


@pytest.fixture
def mock_campaign_response():
    """Sample campaign response data."""
    return {
        "id": "campaign_123",
        "name": "Test Campaign",
        "status": "active",
        "leads_count": 100,
        "opened_count": 45,
        "replied_count": 12,
        "created_at": "2025-11-01T00:00:00Z",
        "started_at": "2025-11-02T00:00:00Z",
    }


@pytest.fixture
def mock_conversation_response():
    """Sample conversation response data."""
    return {
        "thread_id": "thread_123",
        "lead_id": "lead_123",
        "messages": [
            {
                "id": "msg_1",
                "content": "Hello, this is a test message",
                "sender": "user@example.com",
                "timestamp": "2025-11-05T10:00:00Z",
            }
        ],
        "unread_count": 0,
    }


@pytest.fixture
def mock_webhook_response():
    """Sample webhook response data."""
    return {
        "id": "webhook_123",
        "url": "https://example.com/webhook",
        "events": ["lead.created", "campaign.started"],
        "active": True,
        "created_at": "2025-11-05T12:00:00Z",
    }
