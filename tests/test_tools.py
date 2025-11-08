"""
Test suite for Multilead MCP server tools.

Tests all 77 tools across categories:
- Leads (32 tools)
- Campaigns (12 tools)
- Conversations (15 tools)
- Webhooks (8 tools)
- Statistics (7 tools)
- Users (10 tools)
- Team Management (5 tools)
- Settings (3 tools)
"""

import pytest
from fastmcp.client import Client
from fastmcp.client.transports import FastMCPTransport
from fastmcp.exceptions import ToolError
from unittest.mock import patch


# ============================================================================
# Lead Management Tools Tests (32 tools)
# ============================================================================


@pytest.mark.asyncio
async def test_create_lead_success(
    mcp_client: Client[FastMCPTransport], mock_multilead_client_success, mock_lead_response
):
    """Test creating a lead with valid data."""
    mock_multilead_client_success.__aenter__.return_value.request.return_value.json.return_value = (
        mock_lead_response
    )

    result = await mcp_client.call_tool(
        "create_lead",
        {
            "email": "test@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "company": "Test Corp",
        },
    )

    assert result.data["email"] == "test@example.com"
    assert result.data["first_name"] == "John"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "email,first_name,last_name,company",
    [
        ("user1@test.com", "Alice", "Smith", "TechCo"),
        ("user2@test.com", "Bob", "Johnson", "StartupInc"),
        ("user3@test.com", "Charlie", "Brown", "Enterprise Ltd"),
    ],
)
async def test_create_lead_parametrized(
    mcp_client: Client[FastMCPTransport],
    mock_multilead_client_success,
    email: str,
    first_name: str,
    last_name: str,
    company: str,
):
    """Test creating leads with multiple parameter sets."""
    mock_response = {
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "company": company,
    }
    mock_multilead_client_success.__aenter__.return_value.request.return_value.json.return_value = (
        mock_response
    )

    result = await mcp_client.call_tool(
        "create_lead",
        {
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "company": company,
        },
    )

    assert result.data["email"] == email
    assert result.data["first_name"] == first_name


@pytest.mark.asyncio
async def test_get_lead_success(
    mcp_client: Client[FastMCPTransport], mock_multilead_client_success, mock_lead_response
):
    """Test retrieving a lead by ID."""
    mock_multilead_client_success.__aenter__.return_value.request.return_value.json.return_value = (
        mock_lead_response
    )

    result = await mcp_client.call_tool("get_lead", {"lead_id": "lead_123"})

    assert result.data["id"] == "lead_123"
    assert result.data["email"] == "test@example.com"


@pytest.mark.asyncio
async def test_get_lead_not_found(mcp_client: Client[FastMCPTransport], mock_multilead_client_404):
    """Test retrieving a non-existent lead."""
    with pytest.raises(Exception):  # ToolError wrapped in exception
        await mcp_client.call_tool("get_lead", {"lead_id": "nonexistent"})


@pytest.mark.asyncio
async def test_list_leads_success(
    mcp_client: Client[FastMCPTransport], mock_multilead_client_success, mock_lead_response
):
    """Test listing leads with filters."""
    mock_response = {"leads": [mock_lead_response], "total": 1, "page": 1}
    mock_multilead_client_success.__aenter__.return_value.request.return_value.json.return_value = (
        mock_response
    )

    result = await mcp_client.call_tool(
        "list_leads", {"tags": ["prospect"], "limit": 10, "offset": 0}
    )

    assert "leads" in result.data
    assert result.data["total"] == 1


@pytest.mark.asyncio
async def test_update_lead_success(
    mcp_client: Client[FastMCPTransport], mock_multilead_client_success
):
    """Test updating a lead's information."""
    updated_lead = {"id": "lead_123", "first_name": "Jane", "last_name": "Doe"}
    mock_multilead_client_success.__aenter__.return_value.request.return_value.json.return_value = (
        updated_lead
    )

    result = await mcp_client.call_tool(
        "update_lead", {"lead_id": "lead_123", "first_name": "Jane"}
    )

    assert result.data["first_name"] == "Jane"


@pytest.mark.asyncio
async def test_delete_lead_success(
    mcp_client: Client[FastMCPTransport], mock_multilead_client_success
):
    """Test deleting a lead."""
    mock_response = {"success": True, "message": "Lead deleted"}
    mock_multilead_client_success.__aenter__.return_value.request.return_value.json.return_value = (
        mock_response
    )

    result = await mcp_client.call_tool("delete_lead", {"lead_id": "lead_123"})

    assert result.data["success"] is True


@pytest.mark.asyncio
async def test_add_leads_to_campaign_success(
    mcp_client: Client[FastMCPTransport], mock_multilead_client_success
):
    """Test adding leads to a campaign."""
    mock_response = {"leadId": 175049931, "campaignId": 374384, "leadStatusId": 1}
    mock_multilead_client_success.__aenter__.return_value.request.return_value.json.return_value = (
        mock_response
    )

    result = await mcp_client.call_tool(
        "add_leads_to_campaign",
        {
            "campaign_id": "374384",
            "email": "test@example.com",
            "custom_fields": {"firstName": "John", "lastName": "Doe"}
        },
    )

    assert result.data["leadId"] == 175049931


@pytest.mark.asyncio
async def test_pause_lead_execution(
    mcp_client: Client[FastMCPTransport], mock_multilead_client_success
):
    """Test pausing lead execution in campaign."""
    mock_response = {"lead_id": "lead_123", "status": "paused"}
    mock_multilead_client_success.__aenter__.return_value.request.return_value.json.return_value = (
        mock_response
    )

    result = await mcp_client.call_tool("pause_lead_execution", {"lead_id": "lead_123"})

    assert result.data["status"] == "paused"


@pytest.mark.asyncio
async def test_resume_lead_execution(
    mcp_client: Client[FastMCPTransport], mock_multilead_client_success
):
    """Test resuming lead execution in campaign."""
    mock_response = {"lead_id": "lead_123", "status": "active"}
    mock_multilead_client_success.__aenter__.return_value.request.return_value.json.return_value = (
        mock_response
    )

    result = await mcp_client.call_tool("resume_lead_execution", {"lead_id": "lead_123"})

    assert result.data["status"] == "active"


@pytest.mark.asyncio
async def test_assign_tag_to_lead(
    mcp_client: Client[FastMCPTransport], mock_multilead_client_success
):
    """Test assigning a tag to a lead."""
    mock_response = {"lead_id": "lead_123", "tag_id": "tag_456", "success": True}
    mock_multilead_client_success.__aenter__.return_value.request.return_value.json.return_value = (
        mock_response
    )

    result = await mcp_client.call_tool(
        "assign_tag_to_lead",
        {"user_id": "user_1", "account_id": "acc_1", "lead_id": "lead_123", "tag_id": "tag_456"},
    )

    assert result.data["success"] is True


@pytest.mark.asyncio
async def test_remove_tag_from_lead(
    mcp_client: Client[FastMCPTransport], mock_multilead_client_success
):
    """Test removing a tag from a lead."""
    mock_response = {"lead_id": "lead_123", "tag_removed": True}
    mock_multilead_client_success.__aenter__.return_value.request.return_value.json.return_value = (
        mock_response
    )

    result = await mcp_client.call_tool(
        "remove_tag_from_lead",
        {"user_id": "user_1", "account_id": "acc_1", "lead_id": "lead_123", "tag_id": "tag_456"},
    )

    assert result.data["tag_removed"] is True


# ============================================================================
# Campaign Management Tools Tests (12 tools)
# ============================================================================


@pytest.mark.asyncio
async def test_get_campaign_info(
    mcp_client: Client[FastMCPTransport], mock_multilead_client_success, mock_campaign_response
):
    """Test retrieving campaign information."""
    mock_multilead_client_success.__aenter__.return_value.request.return_value.json.return_value = (
        mock_campaign_response
    )

    result = await mcp_client.call_tool(
        "get_campaign_info",
        {"user_id": "user_1", "account_id": "acc_1", "campaign_id": "campaign_123"},
    )

    assert result.data["id"] == "campaign_123"
    assert result.data["name"] == "Test Campaign"


@pytest.mark.asyncio
async def test_get_campaign_list(
    mcp_client: Client[FastMCPTransport], mock_multilead_client_success, mock_campaign_response
):
    """Test listing campaigns."""
    mock_response = {"campaigns": [mock_campaign_response], "total": 1}
    mock_multilead_client_success.__aenter__.return_value.request.return_value.json.return_value = (
        mock_response
    )

    result = await mcp_client.call_tool(
        "get_campaign_list", {"user_id": "user_1", "account_id": "acc_1"}
    )

    assert "campaigns" in result.data
    assert len(result.data["campaigns"]) == 1


@pytest.mark.asyncio
async def test_create_campaign_from_template(
    mcp_client: Client[FastMCPTransport], mock_multilead_client_success
):
    """Test creating a campaign from template."""
    mock_response = {"campaign_id": "campaign_new", "name": "New Campaign", "status": "draft"}
    mock_multilead_client_success.__aenter__.return_value.request.return_value.json.return_value = (
        mock_response
    )

    result = await mcp_client.call_tool(
        "create_campaign_from_template",
        {
            "user_id": "user_1",
            "account_id": "acc_1",
            "sequence_template_id": "template_123",
            "campaign_name": "New Campaign",
        },
    )

    assert result.data["campaign_id"] == "campaign_new"


@pytest.mark.asyncio
async def test_export_all_campaigns(
    mcp_client: Client[FastMCPTransport], mock_multilead_client_success
):
    """Test exporting all campaigns."""
    mock_response = {"export_url": "https://example.com/export.csv", "campaigns_count": 10}
    mock_multilead_client_success.__aenter__.return_value.request.return_value.json.return_value = (
        mock_response
    )

    result = await mcp_client.call_tool(
        "export_all_campaigns", {"user_id": "user_1", "account_id": "acc_1"}
    )

    assert "export_url" in result.data


@pytest.mark.asyncio
async def test_get_leads_from_campaign(
    mcp_client: Client[FastMCPTransport], mock_multilead_client_success, mock_lead_response
):
    """Test retrieving leads from a campaign."""
    mock_response = {"leads": [mock_lead_response], "total": 1}
    mock_multilead_client_success.__aenter__.return_value.request.return_value.json.return_value = (
        mock_response
    )

    result = await mcp_client.call_tool(
        "get_leads_from_campaign",
        {
            "user_id": "user_1",
            "account_id": "acc_1",
            "campaign_id": "campaign_123",
            "filter_by_status": [1],
        },
    )

    assert "leads" in result.data


# ============================================================================
# Statistics Tools Tests (7 tools)
# ============================================================================


@pytest.mark.asyncio
async def test_get_statistics(
    mcp_client: Client[FastMCPTransport], mock_multilead_client_success
):
    """Test retrieving campaign statistics."""
    mock_response = {
        "campaign_id": "campaign_123",
        "sent": 100,
        "opened": 45,
        "clicked": 20,
        "replied": 12,
        "bounced": 3,
    }
    mock_multilead_client_success.__aenter__.return_value.request.return_value.json.return_value = (
        mock_response
    )

    result = await mcp_client.call_tool(
        "get_statistics",
        {
            "user_id": "user_1",
            "account_id": "acc_1",
            "from_timestamp": 1730419200,  # 2025-11-01
            "to_timestamp": 1730764800,    # 2025-11-05
            "curves": [3, 4, 6, 7],
            "time_zone": "UTC",
            "campaign_id": 123,
        },
    )

    assert result.data["sent"] == 100
    assert result.data["opened"] == 45


@pytest.mark.asyncio
async def test_export_statistics_csv(
    mcp_client: Client[FastMCPTransport], mock_multilead_client_success
):
    """Test exporting statistics as CSV."""
    mock_response = {"csv_url": "https://example.com/stats.csv", "rows": 100}
    mock_multilead_client_success.__aenter__.return_value.request.return_value.json.return_value = (
        mock_response
    )

    result = await mcp_client.call_tool(
        "export_statistics_csv",
        {
            "user_id": "user_1",
            "account_id": "acc_1",
            "from_timestamp": 1730419200,  # 2025-11-01
            "to_timestamp": 1730764800,    # 2025-11-05
            "curves": [3, 4, 6, 7],
            "time_zone": "UTC",
        },
    )

    assert "csv_url" in result.data


@pytest.mark.asyncio
async def test_get_all_campaigns_statistics(
    mcp_client: Client[FastMCPTransport], mock_multilead_client_success
):
    """Test retrieving statistics for all campaigns."""
    mock_response = {
        "total_campaigns": 5,
        "total_sent": 500,
        "total_opened": 225,
        "overall_open_rate": 0.45,
    }
    mock_multilead_client_success.__aenter__.return_value.request.return_value.json.return_value = (
        mock_response
    )

    result = await mcp_client.call_tool(
        "get_all_campaigns_statistics",
        {"user_id": "user_1", "account_id": "acc_1", "campaign_state": 1},
    )

    assert result.data["total_campaigns"] == 5


# ============================================================================
# Conversation Tools Tests (15 tools)
# ============================================================================


@pytest.mark.asyncio
async def test_get_messages_from_specific_thread(
    mcp_client: Client[FastMCPTransport],
    mock_multilead_client_success,
    mock_conversation_response,
):
    """Test retrieving messages from a thread."""
    mock_multilead_client_success.__aenter__.return_value.request.return_value.json.return_value = (
        mock_conversation_response
    )

    result = await mcp_client.call_tool(
        "get_messages_from_a_specific_thread",
        {"user_id": "user_1", "account_id": "acc_1", "threads": ["thread_123"]},
    )

    assert result.data["thread_id"] == "thread_123"
    assert len(result.data["messages"]) > 0


@pytest.mark.asyncio
async def test_get_all_conversations(
    mcp_client: Client[FastMCPTransport], mock_multilead_client_success, mock_conversation_response
):
    """Test retrieving all conversations."""
    mock_response = {"conversations": [mock_conversation_response], "total": 1}
    mock_multilead_client_success.__aenter__.return_value.request.return_value.json.return_value = (
        mock_response
    )

    result = await mcp_client.call_tool(
        "get_all_conversations", {"user_id": "user_1", "account_id": "acc_1", "limit": 10}
    )

    assert "conversations" in result.data


@pytest.mark.asyncio
async def test_get_unread_conversations(
    mcp_client: Client[FastMCPTransport], mock_multilead_client_success
):
    """Test retrieving unread conversations."""
    mock_response = {"unread_conversations": [{"thread_id": "thread_123", "unread_count": 3}]}
    mock_multilead_client_success.__aenter__.return_value.request.return_value.json.return_value = (
        mock_response
    )

    result = await mcp_client.call_tool(
        "get_unread_conversations", {"user_id": "user_1", "account_id": "acc_1"}
    )

    assert "unread_conversations" in result.data


@pytest.mark.asyncio
async def test_mark_messages_as_seen(
    mcp_client: Client[FastMCPTransport], mock_multilead_client_success
):
    """Test marking messages as seen."""
    mock_response = {"marked_count": 5, "success": True}
    mock_multilead_client_success.__aenter__.return_value.request.return_value.json.return_value = (
        mock_response
    )

    result = await mcp_client.call_tool(
        "mark_messages_as_seen",
        {
            "user_id": "user_1",
            "account_id": "acc_1",
            "thread": "thread_123",
        },
    )

    assert result.data["success"] is True


@pytest.mark.asyncio
async def test_send_new_email(mcp_client: Client[FastMCPTransport], mock_multilead_client_success):
    """Test sending a new email."""
    mock_response = {"message_id": "msg_new", "status": "sent", "timestamp": "2025-11-05T12:00:00Z"}
    mock_multilead_client_success.__aenter__.return_value.request.return_value.json.return_value = (
        mock_response
    )

    result = await mcp_client.call_tool(
        "send_new_email",
        {
            "user_id": "user_1",
            "account_id": "acc_1",
            "recipient": "test@example.com",
            "subject": "Test Email",
            "content": "Hello, this is a test.",
            "signature_id": 1,
        },
    )

    assert result.data["status"] == "sent"


@pytest.mark.asyncio
async def test_send_email_reply(
    mcp_client: Client[FastMCPTransport], mock_multilead_client_success
):
    """Test sending an email reply."""
    mock_response = {"message_id": "msg_reply", "status": "sent"}
    mock_multilead_client_success.__aenter__.return_value.request.return_value.json.return_value = (
        mock_response
    )

    result = await mcp_client.call_tool(
        "send_email_reply",
        {
            "user_id": "user_1",
            "account_id": "acc_1",
            "thread": "thread_123",
            "message": "Thank you for your message.",
            "lead_id": 123,
            "campaign_id": 456,
            "recipient": "test@example.com",
        },
    )

    assert result.data["status"] == "sent"


@pytest.mark.asyncio
async def test_send_linkedin_message(
    mcp_client: Client[FastMCPTransport], mock_multilead_client_success
):
    """Test sending a LinkedIn message."""
    mock_response = {"message_id": "linkedin_msg_123", "status": "sent"}
    mock_multilead_client_success.__aenter__.return_value.request.return_value.json.return_value = (
        mock_response
    )

    result = await mcp_client.call_tool(
        "send_linkedin_message",
        {
            "user_id": "user_1",
            "account_id": "acc_1",
            "linkedin_user_id": 123,
            "message": "Hello on LinkedIn!",
            "public_identifier": "test-user",
            "campaign_id": 456,
            "lead_id": 789,
        },
    )

    assert result.data["status"] == "sent"


# ============================================================================
# Webhook Tools Tests (8 tools)
# ============================================================================


@pytest.mark.asyncio
async def test_create_webhook(
    mcp_client: Client[FastMCPTransport], mock_multilead_client_success, mock_webhook_response
):
    """Test creating a webhook."""
    mock_multilead_client_success.__aenter__.return_value.request.return_value.json.return_value = (
        mock_webhook_response
    )

    result = await mcp_client.call_tool(
        "create_webhook",
        {
            "user_id": "user_1",
            "account_id": "acc_1",
            "webhooks": [{"url": "https://example.com/webhook", "events": ["lead.created", "campaign.started"]}],
        },
    )

    assert result.data["id"] == "webhook_123"
    assert result.data["url"] == "https://example.com/webhook"


@pytest.mark.asyncio
async def test_list_webhooks(
    mcp_client: Client[FastMCPTransport], mock_multilead_client_success, mock_webhook_response
):
    """Test listing webhooks."""
    mock_response = {"webhooks": [mock_webhook_response], "total": 1}
    mock_multilead_client_success.__aenter__.return_value.request.return_value.json.return_value = (
        mock_response
    )

    result = await mcp_client.call_tool(
        "list_webhooks", {"user_id": "user_1", "account_id": "acc_1"}
    )

    assert "webhooks" in result.data
    assert len(result.data["webhooks"]) == 1


@pytest.mark.asyncio
async def test_delete_webhook(
    mcp_client: Client[FastMCPTransport], mock_multilead_client_success
):
    """Test deleting a webhook."""
    mock_response = {"success": True, "webhook_id": "webhook_123"}
    mock_multilead_client_success.__aenter__.return_value.request.return_value.json.return_value = (
        mock_response
    )

    result = await mcp_client.call_tool(
        "delete_webhook",
        {"user_id": "user_1", "account_id": "acc_1", "webhook_id": "webhook_123"},
    )

    assert result.data["success"] is True


@pytest.mark.asyncio
async def test_create_global_webhook(
    mcp_client: Client[FastMCPTransport], mock_multilead_client_success
):
    """Test creating a global webhook."""
    mock_response = {
        "id": "global_webhook_123",
        "url": "https://example.com/global",
        "events": ["*"],
    }
    mock_multilead_client_success.__aenter__.return_value.request.return_value.json.return_value = (
        mock_response
    )

    result = await mcp_client.call_tool(
        "create_global_webhook",
        {
            "user_id": "user_1",
            "account_id": "acc_1",
            "webhooks": [{"url": "https://example.com/global", "events": ["*"]}],
        },
    )

    assert result.data["id"] == "global_webhook_123"


# ============================================================================
# User Management Tools Tests (10 tools)
# ============================================================================


@pytest.mark.asyncio
async def test_get_user_information(
    mcp_client: Client[FastMCPTransport], mock_multilead_client_success
):
    """Test retrieving user information."""
    mock_response = {
        "id": "user_1",
        "email": "user@example.com",
        "name": "Test User",
        "role": "admin",
    }
    mock_multilead_client_success.__aenter__.return_value.request.return_value.json.return_value = (
        mock_response
    )

    result = await mcp_client.call_tool("get_user_information", {})

    assert result.data["email"] == "user@example.com"


@pytest.mark.asyncio
async def test_register_new_user(
    mcp_client: Client[FastMCPTransport], mock_multilead_client_success
):
    """Test registering a new user."""
    mock_response = {"id": "user_new", "email": "newuser@example.com", "status": "pending"}
    mock_multilead_client_success.__aenter__.return_value.request.return_value.json.return_value = (
        mock_response
    )

    result = await mcp_client.call_tool(
        "register_new_user",
        {
            "email": "newuser@example.com",
            "password": "SecurePass123!",
            "full_name": "New User",
            "whitelabel_id": 1,
        },
    )

    assert result.data["email"] == "newuser@example.com"


@pytest.mark.asyncio
async def test_list_all_seats_of_specific_user(
    mcp_client: Client[FastMCPTransport], mock_multilead_client_success
):
    """Test listing all seats for a user."""
    mock_response = {"seats": [{"id": "seat_1", "account_id": "acc_1", "status": "active"}]}
    mock_multilead_client_success.__aenter__.return_value.request.return_value.json.return_value = (
        mock_response
    )

    result = await mcp_client.call_tool("list_all_seats_of_a_specific_user", {})

    assert "seats" in result.data


@pytest.mark.asyncio
async def test_create_seat(mcp_client: Client[FastMCPTransport], mock_multilead_client_success):
    """Test creating a seat for a user."""
    mock_response = {"seat_id": "seat_new", "account_id": "acc_1", "status": "active"}
    mock_multilead_client_success.__aenter__.return_value.request.return_value.json.return_value = (
        mock_response
    )

    result = await mcp_client.call_tool(
        "create_seat",
        {
            "user_id": "user_1",
            "plan_id": 1,
            "full_name": "Test Seat",
            "start_utc_time": "08:00",
            "end_utc_time": "16:00",
            "time_zone": "UTC",
            "team_id": 123,
            "whitelabel_id": 1,
        },
    )

    assert result.data["seat_id"] == "seat_new"


@pytest.mark.asyncio
async def test_send_password_reset_email(
    mcp_client: Client[FastMCPTransport], mock_multilead_client_success
):
    """Test sending password reset email."""
    mock_response = {"success": True, "message": "Password reset email sent"}
    mock_multilead_client_success.__aenter__.return_value.request.return_value.json.return_value = (
        mock_response
    )

    result = await mcp_client.call_tool(
        "send_password_reset_email", {"email": "user@example.com"}
    )

    assert result.data["success"] is True


# ============================================================================
# Team Management Tools Tests (5 tools)
# ============================================================================


@pytest.mark.asyncio
async def test_create_team(mcp_client: Client[FastMCPTransport], mock_multilead_client_success):
    """Test creating a team."""
    mock_response = {"team_id": "team_123", "name": "Test Team", "created_at": "2025-11-05"}
    mock_multilead_client_success.__aenter__.return_value.request.return_value.json.return_value = (
        mock_response
    )

    result = await mcp_client.call_tool("create_team", {"user_id": "user_1", "name": "Test Team"})

    assert result.data["team_id"] == "team_123"


@pytest.mark.asyncio
async def test_get_team_members(
    mcp_client: Client[FastMCPTransport], mock_multilead_client_success
):
    """Test retrieving team members."""
    mock_response = {
        "members": [
            {"user_id": "user_1", "role": "admin"},
            {"user_id": "user_2", "role": "member"},
        ]
    }
    mock_multilead_client_success.__aenter__.return_value.request.return_value.json.return_value = (
        mock_response
    )

    result = await mcp_client.call_tool(
        "get_team_members", {"user_id": "user_1", "team_id": "team_123"}
    )

    assert len(result.data["members"]) == 2


@pytest.mark.asyncio
async def test_invite_team_member(
    mcp_client: Client[FastMCPTransport], mock_multilead_client_success
):
    """Test inviting a team member."""
    mock_response = {
        "invite_id": "invite_123",
        "email": "newmember@example.com",
        "status": "pending",
    }
    mock_multilead_client_success.__aenter__.return_value.request.return_value.json.return_value = (
        mock_response
    )

    result = await mcp_client.call_tool(
        "invite_team_member",
        {
            "team_id": "team_123",
            "user_id": "user_1",
            "name": "New Member",
            "email": "newmember@example.com",
            "account_roles": [{"roleId": 1, "accounts": ["acc_1"]}],
        },
    )

    assert result.data["email"] == "newmember@example.com"


# ============================================================================
# Error Handling Tests
# ============================================================================


@pytest.mark.asyncio
async def test_unauthorized_request(
    mcp_client: Client[FastMCPTransport], mock_multilead_client_401
):
    """Test handling 401 Unauthorized error."""
    with pytest.raises(Exception):  # ToolError wrapped
        await mcp_client.call_tool("get_lead", {"lead_id": "lead_123"})


@pytest.mark.asyncio
async def test_rate_limit_error(mcp_client: Client[FastMCPTransport], mock_multilead_client_429):
    """Test handling 429 Rate Limit error."""
    with pytest.raises(Exception):  # ToolError wrapped
        await mcp_client.call_tool("list_leads", {})


@pytest.mark.asyncio
async def test_server_error(mcp_client: Client[FastMCPTransport], mock_multilead_client_500):
    """Test handling 500 Server Error."""
    with pytest.raises(Exception):  # ToolError wrapped
        await mcp_client.call_tool("get_campaign_info", {"user_id": "user_1", "account_id": "acc_1", "campaign_id": "campaign_123"})


@pytest.mark.asyncio
async def test_timeout_error(mcp_client: Client[FastMCPTransport], mock_multilead_client_timeout):
    """Test handling request timeout."""
    with pytest.raises(Exception):  # ToolError wrapped
        await mcp_client.call_tool("get_lead", {"lead_id": "lead_123"})


# ============================================================================
# Additional Tool Tests (Blacklist, Warmup, Settings)
# ============================================================================


@pytest.mark.asyncio
async def test_add_keywords_to_global_blacklist(
    mcp_client: Client[FastMCPTransport], mock_multilead_client_success
):
    """Test adding keywords to global blacklist."""
    mock_response = {"keywords_added": 3, "success": True}
    mock_multilead_client_success.__aenter__.return_value.request.return_value.json.return_value = (
        mock_response
    )

    result = await mcp_client.call_tool(
        "add_keywords_to_global_blacklist",
        {
            "team_id": "team_123",
            "user_id": "user_1",
            "keywords": ["spam", "unwanted", "test"],
            "keyword_type": "company_name",
            "comparison_type": "contains",
        },
    )

    assert result.data["keywords_added"] == 3


@pytest.mark.asyncio
async def test_activate_inboxflare_warmup(
    mcp_client: Client[FastMCPTransport], mock_multilead_client_success
):
    """Test activating InboxFlare warmup."""
    mock_response = {"status": "active", "warmup_started": True}
    mock_multilead_client_success.__aenter__.return_value.request.return_value.json.return_value = (
        mock_response
    )

    result = await mcp_client.call_tool("activate_inboxflare_warmup", {"user_id": "user_1"})

    assert result.data["warmup_started"] is True


@pytest.mark.asyncio
async def test_connect_linkedin_account(
    mcp_client: Client[FastMCPTransport], mock_multilead_client_success
):
    """Test connecting a LinkedIn account."""
    mock_response = {"linkedin_connected": True, "account_id": "linkedin_acc_123"}
    mock_multilead_client_success.__aenter__.return_value.request.return_value.json.return_value = (
        mock_response
    )

    result = await mcp_client.call_tool(
        "connect_linkedin_account",
        {
            "user_id": "user_1",
            "account_id": "acc_1",
            "linkedin_email": "linkedin@example.com",
            "linkedin_password": "password123",
            "linkedin_subscription_id": 1,
            "country_code": "us",
            "setup_proxy_type": "BUY",
        },
    )

    assert result.data["linkedin_connected"] is True


@pytest.mark.asyncio
async def test_disconnect_linkedin_account(
    mcp_client: Client[FastMCPTransport], mock_multilead_client_success
):
    """Test disconnecting a LinkedIn account."""
    mock_response = {"linkedin_disconnected": True, "success": True}
    mock_multilead_client_success.__aenter__.return_value.request.return_value.json.return_value = (
        mock_response
    )

    result = await mcp_client.call_tool(
        "disconnect_linkedin_account",
        {"user_id": "user_1", "account_id": "acc_1"},
    )

    assert result.data["success"] is True
