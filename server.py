"""
Multilead Open API MCP Server

A comprehensive FastMCP server providing access to the Multilead Open API with 74 endpoints
for lead management, campaigns, conversations, webhooks, and analytics.

API Documentation: https://documenter.getpostman.com/view/7428744/UV5ZAGMg
Base URL: https://api.multilead.io/api/open-api/v1
"""

import json
import os
from typing import Any, Dict, List, Optional
from datetime import datetime

import httpx
from dotenv import load_dotenv
from fastmcp import FastMCP
from fastmcp.exceptions import ToolError

try:
    from fastmcp.server.middleware.response_limiting import ResponseLimitingMiddleware
    HAS_RESPONSE_LIMITING = True
except ImportError:
    HAS_RESPONSE_LIMITING = False
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()

# Initialize FastMCP server
mcp = FastMCP(
    name="Multilead Open API",
    instructions="""
    This server provides comprehensive access to the Multilead Open API for managing:

    **Lead Management (14 endpoints)**:
    - Create, retrieve, update, and delete leads
    - Add leads to campaigns, pause/resume execution
    - Manage lead tags and track lead status
    - Get leads from campaigns, threads, and seats

    **Campaign Management (6 endpoints)**:
    - Create campaigns from templates
    - Get campaign info and campaign lists
    - Export campaigns and manage campaign leads

    **Users & Seats (15 endpoints)**:
    - User registration, authentication, and password management
    - Create and manage seats (accounts)
    - Connect/disconnect LinkedIn accounts
    - Transfer credits between seats

    **Conversations (12 endpoints)**:
    - Access email thread conversations
    - Retrieve message history and metadata
    - Send emails and LinkedIn messages
    - Mark messages as seen and manage threads

    **Webhooks (6 endpoints)**:
    - Register webhook endpoints for real-time events
    - Create and delete seat-level and global webhooks
    - Subscribe to lead, campaign, and conversation events

    **Seats (3 endpoints)**:
    - Manage seat tags and lead sources
    - Return leads to campaigns from seats

    **Statistics (4 endpoints)**:
    - Campaign statistics and performance metrics
    - Export statistics as CSV
    - All campaigns statistics overview

    **Blacklist (4 endpoints)**:
    - Global and seat-level keyword blacklists
    - Add keywords and upload blacklist CSVs

    **Warmup (1 endpoint)**:
    - Activate InboxFlare email warmup

    **Team Management (6 endpoints)**:
    - Create teams and manage team members
    - Invite members and assign roles
    - Remove team members

    **Settings (1 endpoint)**:
    - Resolve identity type IDs to descriptions

    All endpoints require authentication via API key. The server handles rate limiting,
    retries, and error responses automatically.
    """,
    version="1.0.0",
)

if HAS_RESPONSE_LIMITING:
    mcp.add_middleware(ResponseLimitingMiddleware(max_size=100_000))


# Configuration
class MultileadConfig:
    """Configuration for Multilead API client"""

    def __init__(self):
        self.api_key = os.getenv("MULTILEAD_API_KEY")
        self.base_url = os.getenv("MULTILEAD_BASE_URL", "https://api.multilead.io/api/open-api/v1")
        self.timeout = int(os.getenv("MULTILEAD_TIMEOUT", "30"))
        self.debug = os.getenv("MULTILEAD_DEBUG", "false").lower() == "true"

        if not self.api_key:
            raise ValueError(
                "MULTILEAD_API_KEY environment variable is required. "
                "Please set it in your .env file."
            )


config = MultileadConfig()


# HTTP Client with authentication
class MultileadClient:
    """HTTP client for Multilead API with authentication and error handling"""

    def __init__(self):
        self.base_url = config.base_url.rstrip("/")
        self.headers = {
            "Authorization": config.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        self.timeout = config.timeout

    async def request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make an authenticated request to the Multilead API

        Args:
            method: HTTP method (GET, POST, PUT, PATCH, DELETE)
            endpoint: API endpoint path (without base URL)
            params: Query parameters
            json_data: JSON request body

        Returns:
            Response data as dictionary

        Raises:
            ToolError: If the request fails
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    params=params,
                    json=json_data,
                )

                # Handle specific HTTP errors
                if response.status_code == 401:
                    raise ToolError(
                        "Authentication failed. Please check your MULTILEAD_API_KEY. "
                        "Get your API key from: https://app.multilead.co/settings/api"
                    )
                elif response.status_code == 403:
                    raise ToolError(
                        "Access forbidden. Your API key may not have permission for this resource."
                    )
                elif response.status_code == 404:
                    raise ToolError(f"Resource not found: {endpoint}")
                elif response.status_code == 429:
                    raise ToolError(
                        "Rate limit exceeded. Please wait before making more requests."
                    )
                elif response.status_code >= 500:
                    raise ToolError(
                        f"Multilead API server error ({response.status_code}). "
                        "Please try again later."
                    )

                response.raise_for_status()

                # Return JSON response or empty dict for 204 No Content
                if response.status_code == 204:
                    return {"success": True, "message": "Operation completed successfully"}

                return response.json()

        except httpx.TimeoutException:
            raise ToolError(
                f"Request timed out after {self.timeout} seconds. "
                "Try increasing MULTILEAD_TIMEOUT in your .env file."
            )
        except httpx.RequestError as e:
            raise ToolError(f"Network error while connecting to Multilead API: {str(e)}")
        except Exception as e:
            if isinstance(e, ToolError):
                raise
            raise ToolError(f"Unexpected error: {str(e)}")


# Initialize global client
client = MultileadClient()


# ============================================================================
# HTTP Production Features
# ============================================================================

@mcp.custom_route("/health", methods=["GET"])
async def health_check(request):
    """
    Health check endpoint for monitoring and load balancers

    Returns:
        JSON response with server status and basic info
    """
    from starlette.responses import JSONResponse

    health_data = {
        "status": "healthy",
        "service": "multilead-mcp",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "transport": "http" if os.getenv("TRANSPORT", "stdio") == "http" else "stdio",
    }

    # Optional: Check Multilead API connectivity
    try:
        if config.api_key:
            health_data["api_configured"] = True
        else:
            health_data["api_configured"] = False
            health_data["status"] = "degraded"
            health_data["message"] = "API key not configured"
    except Exception as e:
        health_data["status"] = "unhealthy"
        health_data["error"] = str(e)

    status_code = 200 if health_data["status"] == "healthy" else 503

    return JSONResponse(health_data, status_code=status_code)


# ============================================================================
# Production Middleware
# ============================================================================

# Logging Configuration
import logging
from logging.handlers import RotatingFileHandler
import time
from collections import defaultdict
from datetime import timedelta

# Configure structured logging
def setup_logging():
    """Configure production-ready logging with rotation"""
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    log_format = os.getenv("LOG_FORMAT", "json")  # json or text

    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(__file__), "logs")
    os.makedirs(log_dir, exist_ok=True)

    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level, logging.INFO))

    # Console handler for development
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level, logging.INFO))

    if log_format == "json":
        # JSON formatter for production
        import json as json_module
        class JsonFormatter(logging.Formatter):
            def format(self, record):
                log_data = {
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "level": record.levelname,
                    "logger": record.name,
                    "message": record.getMessage(),
                    "module": record.module,
                    "function": record.funcName,
                    "line": record.lineno,
                }
                if record.exc_info:
                    log_data["exception"] = self.formatException(record.exc_info)
                return json_module.dumps(log_data)

        console_handler.setFormatter(JsonFormatter())
    else:
        # Text formatter for development
        text_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(text_formatter)

    logger.addHandler(console_handler)

    # File handler with rotation for production
    if os.getenv("TRANSPORT", "stdio") == "http":
        file_handler = RotatingFileHandler(
            os.path.join(log_dir, "multilead-mcp.log"),
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(getattr(logging, log_level, logging.INFO))
        file_handler.setFormatter(JsonFormatter() if log_format == "json" else text_formatter)
        logger.addHandler(file_handler)

    return logger

logger = setup_logging()


# Rate Limiting Middleware
class RateLimiter:
    """Simple in-memory rate limiter for HTTP transport"""

    def __init__(self, requests_per_minute: int = 100, requests_per_hour: int = 1000):
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.minute_buckets = defaultdict(list)
        self.hour_buckets = defaultdict(list)

    def is_allowed(self, identifier: str) -> tuple[bool, str]:
        """
        Check if request is allowed based on rate limits

        Args:
            identifier: Client identifier (IP address, API key, etc.)

        Returns:
            Tuple of (allowed: bool, message: str)
        """
        now = time.time()
        minute_ago = now - 60
        hour_ago = now - 3600

        # Clean old entries
        self.minute_buckets[identifier] = [
            t for t in self.minute_buckets[identifier] if t > minute_ago
        ]
        self.hour_buckets[identifier] = [
            t for t in self.hour_buckets[identifier] if t > hour_ago
        ]

        # Check limits
        minute_count = len(self.minute_buckets[identifier])
        hour_count = len(self.hour_buckets[identifier])

        if minute_count >= self.requests_per_minute:
            return False, f"Rate limit exceeded: {self.requests_per_minute} requests per minute"

        if hour_count >= self.requests_per_hour:
            return False, f"Rate limit exceeded: {self.requests_per_hour} requests per hour"

        # Record request
        self.minute_buckets[identifier].append(now)
        self.hour_buckets[identifier].append(now)

        return True, ""

# Initialize rate limiter
rate_limiter = RateLimiter(
    requests_per_minute=int(os.getenv("RATE_LIMIT_PER_MINUTE", "100")),
    requests_per_hour=int(os.getenv("RATE_LIMIT_PER_HOUR", "1000"))
)


# NOTE: Middleware has been removed due to FastMCP compatibility issues.
# FastMCP does not support @mcp.middleware("http") decorator pattern.
# For HTTP-specific middleware, use Starlette middleware when creating the HTTP app.
# See docs/deployment/MIDDLEWARE_IMPLEMENTATION.md for proper implementation.

# Logging, rate limiting, and error handling should be implemented using
# Starlette middleware patterns when creating the HTTP app at the bottom of this file.


# ============================================================================
# Pydantic models for type validation
# ============================================================================
class LeadCreate(BaseModel):
    """Model for creating a new lead"""

    email: str = Field(..., description="Lead email address (required)")
    first_name: Optional[str] = Field(None, description="Lead first name")
    last_name: Optional[str] = Field(None, description="Lead last name")
    company: Optional[str] = Field(None, description="Company name")
    title: Optional[str] = Field(None, description="Job title")
    phone: Optional[str] = Field(None, description="Phone number")
    tags: Optional[List[str]] = Field(None, description="List of tags to assign")
    custom_fields: Optional[Dict[str, Any]] = Field(
        None, description="Custom field key-value pairs"
    )


class LeadFilter(BaseModel):
    """Model for filtering leads"""

    tags: Optional[List[str]] = Field(None, description="Filter by tags")
    company: Optional[str] = Field(None, description="Filter by company name")
    created_after: Optional[str] = Field(None, description="ISO 8601 datetime string")
    created_before: Optional[str] = Field(None, description="ISO 8601 datetime string")
    limit: Optional[int] = Field(100, description="Number of results to return", ge=1, le=1000)
    offset: Optional[int] = Field(0, description="Pagination offset", ge=0)


# ============================================================================
# TOOLS - Example implementations (template for 74 endpoints)
# ============================================================================


@mcp.tool()
async def create_lead(
    email: str,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    company: Optional[str] = None,
    title: Optional[str] = None,
    phone: Optional[str] = None,
    tags: Optional[List[str]] = None,
    custom_fields: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Create a new lead in Multilead

    Note: This endpoint may not be available in all Multilead API versions. Use campaign-scoped lead tools (e.g., get_leads_from_campaign) as an alternative.

    Args:
        email: Lead email address (required)
        first_name: Lead first name
        last_name: Lead last name
        company: Company name
        title: Job title
        phone: Phone number
        tags: List of tags to assign
        custom_fields: Custom field key-value pairs

    Returns:
        Created lead object with ID and metadata
    """
    lead_data = {
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "company": company,
        "title": title,
        "phone": phone,
        "tags": tags or [],
        "custom_fields": custom_fields or {},
    }

    # Remove None values
    lead_data = {k: v for k, v in lead_data.items() if v is not None}

    result = await client.request("POST", "/v1/leads", json_data=lead_data)
    return result


@mcp.tool()
async def get_lead(lead_id: str) -> Dict[str, Any]:
    """
    Retrieve a lead by ID

    Note: This endpoint may not be available in all Multilead API versions. Use campaign-scoped lead tools (e.g., get_leads_from_campaign) as an alternative.

    Args:
        lead_id: The unique identifier of the lead

    Returns:
        Lead object with all properties, tags, and custom fields
    """
    result = await client.request("GET", f"/v1/leads/{lead_id}")
    return result


@mcp.tool()
async def list_leads(
    tags: Optional[List[str]] = None,
    company: Optional[str] = None,
    created_after: Optional[str] = None,
    created_before: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
) -> Dict[str, Any]:
    """
    List and filter leads with pagination

    Note: This endpoint may not be available in all Multilead API versions. Use campaign-scoped lead tools (e.g., get_leads_from_campaign) as an alternative.

    Args:
        tags: Filter by tags (optional)
        company: Filter by company name (optional)
        created_after: Filter leads created after this ISO 8601 datetime
        created_before: Filter leads created before this ISO 8601 datetime
        limit: Number of results to return (1-1000, default: 100)
        offset: Pagination offset (default: 0)

    Returns:
        List of leads matching the filter criteria with pagination metadata
    """
    params = {
        "limit": limit,
        "offset": offset,
    }

    if tags:
        params["tags"] = ",".join(tags)
    if company:
        params["company"] = company
    if created_after:
        params["created_after"] = created_after
    if created_before:
        params["created_before"] = created_before

    result = await client.request("GET", "/v1/leads", params=params)
    return result


@mcp.tool()
async def update_lead(
    lead_id: str,
    email: Optional[str] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    company: Optional[str] = None,
    title: Optional[str] = None,
    phone: Optional[str] = None,
    tags: Optional[List[str]] = None,
    custom_fields: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Update an existing lead's properties

    Note: This endpoint may not be available in all Multilead API versions. Use campaign-scoped lead tools (e.g., get_leads_from_campaign) as an alternative.

    Args:
        lead_id: The unique identifier of the lead
        email: New email address
        first_name: New first name
        last_name: New last name
        company: New company name
        title: New job title
        phone: New phone number
        tags: New list of tags (replaces existing tags)
        custom_fields: New custom fields (merges with existing)

    Returns:
        Updated lead object
    """
    update_data = {
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "company": company,
        "title": title,
        "phone": phone,
        "tags": tags,
        "custom_fields": custom_fields,
    }

    # Remove None values
    update_data = {k: v for k, v in update_data.items() if v is not None}

    if not update_data:
        raise ToolError("At least one field must be provided to update")

    result = await client.request("PUT", f"/v1/leads/{lead_id}", json_data=update_data)
    return result


@mcp.tool()
async def delete_lead(lead_id: str) -> Dict[str, Any]:
    """
    Delete a lead by ID

    Note: This endpoint may not be available in all Multilead API versions. Use campaign-scoped lead tools (e.g., get_leads_from_campaign) as an alternative.

    Args:
        lead_id: The unique identifier of the lead to delete

    Returns:
        Success confirmation message
    """
    result = await client.request("DELETE", f"/v1/leads/{lead_id}")
    return result


# ============================================================================

# ============================================================================
# LEADS TOOLS - Additional endpoints (9 new tools)
# ============================================================================


@mcp.tool()
async def add_leads_to_campaign(
    campaign_id: str,
    profile_url: Optional[str] = None,
    email: Optional[str] = None,
    custom_fields: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Add a new lead to a selected campaign

    Either profileUrl or email is required. All other fields can be provided in custom_fields.

    Args:
        campaign_id: The ID of the campaign to add the lead to
        profile_url: LinkedIn profile URL of the lead (required if email not provided)
        email: Email address of the lead (required if profile_url not provided)
        custom_fields: Additional custom fields for the lead (e.g., {"first_name": "John", "company": "Acme"})

    Returns:
        Created lead information

    Example:
        add_leads_to_campaign(
            campaign_id="12345",
            email="lead@example.com",
            custom_fields={"first_name": "John", "company": "Acme Corp"}
        )
    """
    if not profile_url and not email:
        raise ToolError("Either profile_url or email must be provided")

    lead_data = {}
    if profile_url:
        lead_data["profileUrl"] = profile_url
    if email:
        lead_data["email"] = email

    # Add custom fields if provided
    if custom_fields:
        lead_data.update(custom_fields)

    result = await client.request(
        "POST", f"/campaign/{campaign_id}/leads", json_data=lead_data
    )
    return result


@mcp.tool()
async def update_lead_in_campaign(
    campaign_id: str,
    lead_id: str,
    linkedin_account_id: str,
    changed_values: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Update one or more variables for a lead in a specified campaign and LinkedIn account

    This updates lead fields including built-in fields (businessEmail, etc.) and custom variables.

    Args:
        campaign_id: The ID of the campaign
        lead_id: The ID of the lead to update
        linkedin_account_id: The LinkedIn account ID
        changed_values: Dictionary of field names and new values to update
            Can include built-in fields like "businessEmail" or custom fields

    Returns:
        Updated lead information

    Example:
        update_lead_in_campaign(
            campaign_id="12345",
            lead_id="67890",
            linkedin_account_id="2",
            changed_values={
                "businessEmail": "john.smith@company.com",
                "custom-variable": "custom value"
            }
        )
    """
    update_data = {
        "campaignId": int(campaign_id),
        "linkedinAccountId": int(linkedin_account_id),
        "changedValues": changed_values,
    }

    result = await client.request(
        "PATCH",
        f"/api/open-api/v2/campaigns/{campaign_id}/leads/{lead_id}",
        json_data=update_data,
    )
    return result


@mcp.tool()
async def get_leads_from_thread(
    user_id: str, account_id: str, thread_id: str
) -> Dict[str, Any]:
    """
    Retrieve leads who are part of a specific conversation thread

    Args:
        user_id: The ID of the user
        account_id: The ID of the account (seat)
        thread_id: The ID of the conversation thread

    Returns:
        List of leads belonging to the thread
    """
    result = await client.request(
        "GET",
        f"/users/{user_id}/accounts/{account_id}/conversations/{thread_id}/belonged_leads",
    )
    return result


@mcp.tool()
async def get_tags_for_leads(
    user_id: str, account_id: str, lead_ids: List[str]
) -> Dict[str, Any]:
    """
    Retrieve tags for specific leads

    Args:
        user_id: The ID of the user
        account_id: The ID of the account (seat)
        lead_ids: List of lead IDs whose tags you want to retrieve

    Returns:
        Tags associated with the specified leads
    """
    params = {"leadIds": f"[{','.join(lead_ids)}]"}

    result = await client.request(
        "GET", f"/users/{user_id}/accounts/{account_id}/leads/tags", params=params
    )
    return result


@mcp.tool()
async def assign_tag_to_lead(
    user_id: str, account_id: str, lead_id: str, tag_id: str
) -> Dict[str, Any]:
    """
    Add a new tag to a specific lead

    Args:
        user_id: The ID of the user
        account_id: The ID of the account (seat)
        lead_id: The ID of the lead
        tag_id: The ID of the tag to assign

    Returns:
        Confirmation of tag assignment
    """
    result = await client.request(
        "POST",
        f"/users/{user_id}/accounts/{account_id}/leads/{lead_id}/tags/{tag_id}",
    )
    return result


@mcp.tool()
async def remove_tag_from_lead(
    user_id: str, account_id: str, lead_id: str, tag_id: str
) -> Dict[str, Any]:
    """
    Remove a specific tag from a specific lead

    Args:
        user_id: The ID of the user
        account_id: The ID of the account (seat)
        lead_id: The ID of the lead
        tag_id: The ID of the tag to remove

    Returns:
        Confirmation of tag removal
    """
    result = await client.request(
        "DELETE",
        f"/users/{user_id}/accounts/{account_id}/leads/{lead_id}/tags/{tag_id}",
    )
    return result


@mcp.tool()
async def get_linkedin_user_info(
    user_id: str, account_id: str, linkedin_user_id: str
) -> Dict[str, Any]:
    """
    Retrieve LinkedIn profile information for a specific user

    This returns profile information if you previously started a conversation with them.

    Args:
        user_id: The ID of the user
        account_id: The ID of the account (seat)
        linkedin_user_id: The LinkedIn user ID

    Returns:
        LinkedIn profile information including name, headline, company, etc.
    """
    result = await client.request(
        "GET",
        f"/users/{user_id}/accounts/{account_id}/linkedin_users/{linkedin_user_id}",
    )
    return result


@mcp.tool()
async def pause_lead_execution(lead_id: str) -> Dict[str, Any]:
    """
    Pause the execution of campaign steps for a specific lead

    This pauses all upcoming steps in the campaign workflow for this lead.

    Args:
        lead_id: The ID of the lead to pause

    Returns:
        Confirmation of lead pause
    """
    result = await client.request("PATCH", f"/leads/{lead_id}/pause")
    return result


@mcp.tool()
async def resume_lead_execution(lead_id: str) -> Dict[str, Any]:
    """
    Resume the execution of campaign steps for a specific lead

    This resumes the campaign workflow for a previously paused lead.

    Args:
        lead_id: The ID of the lead to resume

    Returns:
        Confirmation of lead resumption
    """
    result = await client.request("PATCH", f"/leads/{lead_id}/continue")
    return result


@mcp.tool()
async def get_leads_from_campaign(
    user_id: str,
    account_id: str,
    campaign_id: str,
    search: Optional[str] = None,
    filter_by_verified_emails: Optional[bool] = None,
    filter_by_not_verified_emails: Optional[bool] = None,
    filter_by_status: Optional[List[int]] = None,
    filter_by_connection_degree: Optional[List[int]] = None,
    filter_by_current_step: Optional[List[int]] = None,
    filter_by_name: Optional[str] = None,
    filter_by_company: Optional[str] = None,
    filter_by_occupation: Optional[str] = None,
    filter_by_headline: Optional[str] = None,
    filter_by_out_of_office: Optional[bool] = None,
    filter_by_step_change_timestamp: Optional[int] = None,
    filter_by_selected_leads: Optional[List[int]] = None,
    limit: int = 30,
    offset: int = 0,
) -> Dict[str, Any]:
    """
    Retrieve leads from a specific campaign with advanced filtering

    Supports 7 groups of filters with OR logic within groups and AND logic between groups:
    1. Advanced filters (name, company, occupation, headline)
    2. Status filters (status, connection degree, out of office)
    3. Email verification filters
    4. Current step filter
    5. Selected leads filter
    6. Step change timestamp filter
    7. General search filter

    Args:
        user_id: The ID of the user
        account_id: The ID of the account (seat)
        campaign_id: The ID of the campaign
        search: Search leads by fullName, email, company, headline, etc.
        filter_by_verified_emails: Filter leads with verified emails
        filter_by_not_verified_emails: Filter leads without verified emails
        filter_by_status: Filter by status ([1]=Discovered, [2]=Connection pending,
            [3]=Connected not replied, [4]=Replied)
        filter_by_connection_degree: Used with filter_by_status=[4] for additional
            status filtering ([1]=replied connected, [2,3]=replied not connected)
        filter_by_current_step: Filter leads on specific campaign steps
        filter_by_name: Filter leads whose names contain this value
        filter_by_company: Filter leads whose company contains this value
        filter_by_occupation: Filter leads whose occupation contains this value
        filter_by_headline: Filter leads whose headline contains this value
        filter_by_out_of_office: Filter leads with "Out of office" status
        filter_by_step_change_timestamp: Filter leads with stepChangeTimestamp greater than this
        filter_by_selected_leads: Retrieve specific leads by their IDs
        limit: Number of results to return (default: 30)
        offset: Pagination offset (default: 0)

    Returns:
        List of leads matching the filter criteria with pagination metadata

    Example:
        get_leads_from_campaign(
            user_id="123",
            account_id="456",
            campaign_id="789",
            filter_by_status=[4],
            filter_by_connection_degree=[1],
            filter_by_verified_emails=True,
            limit=50
        )
    """
    params: Dict[str, Any] = {"limit": limit, "offset": offset}

    if search:
        params["search"] = search
    if filter_by_verified_emails is not None:
        params["filterByVerifiedEmails"] = str(filter_by_verified_emails).lower()
    if filter_by_not_verified_emails is not None:
        params["filterByNotVerifiedEmails"] = str(filter_by_not_verified_emails).lower()
    if filter_by_status:
        params["filterByStatus"] = f"[{','.join(map(str, filter_by_status))}]"
    if filter_by_connection_degree:
        params["filterByConnectionDegree"] = (
            f"[{','.join(map(str, filter_by_connection_degree))}]"
        )
    if filter_by_current_step:
        params["filterByCurrentStep"] = (
            f"[{','.join(map(str, filter_by_current_step))}]"
        )
    if filter_by_name:
        params["filterByName"] = filter_by_name
    if filter_by_company:
        params["filterByCompany"] = filter_by_company
    if filter_by_occupation:
        params["filterByOccupation"] = filter_by_occupation
    if filter_by_headline:
        params["filterByHeadline"] = filter_by_headline
    if filter_by_out_of_office is not None:
        params["filterByOutOfOffice"] = str(filter_by_out_of_office).lower()
    if filter_by_step_change_timestamp:
        params["filterByStepChangeTimestamp"] = filter_by_step_change_timestamp
    if filter_by_selected_leads:
        params["filterBySelectedLeads"] = (
            f"[{','.join(map(str, filter_by_selected_leads))}]"
        )

    result = await client.request(
        "GET",
        f"/users/{user_id}/accounts/{account_id}/campaigns/{campaign_id}/leads",
        params=params,
    )
    return result


@mcp.tool()
async def get_tags_for_seat(user_id: str, account_id: str) -> Dict[str, Any]:
    """
    Retrieve all tags from a specific seat (account)

    Args:
        user_id: The ID of the user
        account_id: The ID of the account (seat)

    Returns:
        List of all tags for the seat
    """
    result = await client.request(
        "GET", f"/users/{user_id}/accounts/{account_id}/tags"
    )
    return result


@mcp.tool()
async def create_tag(
    user_id: str, account_id: str, tag_name: str
) -> Dict[str, Any]:
    """
    Create a new tag for a specific seat (account)

    Args:
        user_id: The ID of the user
        account_id: The ID of the account (seat)
        tag_name: Name of the tag to create

    Returns:
        Created tag information including tag ID
    """
    tag_data = {"name": tag_name}

    result = await client.request(
        "POST", f"/users/{user_id}/accounts/{account_id}/tags", json_data=tag_data
    )
    return result


@mcp.tool()
async def return_lead_to_campaign(
    user_id: str,
    account_id: str,
    lead_id: str,
    target_campaign_id: str,
    scheduled_time: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Return a specific lead to a specific campaign

    This action happens immediately unless a scheduled time is provided.

    Args:
        user_id: The ID of the user
        account_id: The ID of the account (seat)
        lead_id: The ID of the lead to move
        target_campaign_id: The ID of the campaign to return the lead to
        scheduled_time: Optional ISO 8601 datetime to schedule the action

    Returns:
        Confirmation of lead transfer
    """
    transfer_data = {"campaignId": target_campaign_id}

    if scheduled_time:
        transfer_data["scheduledTime"] = scheduled_time

    result = await client.request(
        "POST",
        f"/users/{user_id}/accounts/{account_id}/leads/{lead_id}/change_campaign",
        json_data=transfer_data,
    )
    return result


@mcp.tool()
async def get_leads_from_seat(
    user_id: str,
    account_id: str,
    search: Optional[str] = None,
    filter_by_verified_emails: Optional[bool] = None,
    filter_by_not_verified_emails: Optional[bool] = None,
    filter_by_status: Optional[List[int]] = None,
    filter_by_connection_degree: Optional[List[int]] = None,
    filter_by_name: Optional[str] = None,
    filter_by_company: Optional[str] = None,
    filter_by_occupation: Optional[str] = None,
    filter_by_headline: Optional[str] = None,
    filter_by_out_of_office: Optional[bool] = None,
    filter_by_step_change_timestamp: Optional[int] = None,
    filter_by_selected_leads: Optional[List[int]] = None,
    limit: int = 30,
    offset: int = 0,
) -> Dict[str, Any]:
    """
    Retrieve leads from a specific seat (account) with advanced filtering

    Supports 6 groups of filters with OR logic within groups and AND logic between groups:
    1. Advanced filters (name, company, occupation, headline)
    2. Status filters (status, connection degree, out of office)
    3. Email verification filters
    4. Selected leads filter
    5. Step change timestamp filter
    6. General search filter

    Args:
        user_id: The ID of the user
        account_id: The ID of the account (seat)
        search: Search leads by fullName, email, company, headline, etc.
        filter_by_verified_emails: Filter leads with verified emails
        filter_by_not_verified_emails: Filter leads without verified emails
        filter_by_status: Filter by status ([1]=Discovered, [2]=Connection pending,
            [3]=Connected not replied, [4]=Replied)
        filter_by_connection_degree: Used with filter_by_status=[4] for additional
            status filtering ([1]=replied connected, [2,3]=replied not connected)
        filter_by_name: Filter leads whose names contain this value
        filter_by_company: Filter leads whose company contains this value
        filter_by_occupation: Filter leads whose occupation contains this value
        filter_by_headline: Filter leads whose headline contains this value
        filter_by_out_of_office: Filter leads with "Out of office" status
        filter_by_step_change_timestamp: Filter leads with stepChangeTimestamp greater than this
        filter_by_selected_leads: Retrieve specific leads by their IDs
        limit: Number of results to return (default: 30)
        offset: Pagination offset (default: 0)

    Returns:
        List of leads from the seat matching the filter criteria

    Example:
        get_leads_from_seat(
            user_id="123",
            account_id="456",
            filter_by_company="Acme Corp",
            filter_by_verified_emails=True,
            limit=100
        )
    """
    params: Dict[str, Any] = {"limit": limit, "offset": offset}

    if search:
        params["search"] = search
    if filter_by_verified_emails is not None:
        params["filterByVerifiedEmails"] = str(filter_by_verified_emails).lower()
    if filter_by_not_verified_emails is not None:
        params["filterByNotVerifiedEmails"] = str(filter_by_not_verified_emails).lower()
    if filter_by_status:
        params["filterByStatus"] = f"[{','.join(map(str, filter_by_status))}]"
    if filter_by_connection_degree:
        params["filterByConnectionDegree"] = (
            f"[{','.join(map(str, filter_by_connection_degree))}]"
        )
    if filter_by_name:
        params["filterByName"] = filter_by_name
    if filter_by_company:
        params["filterByCompany"] = filter_by_company
    if filter_by_occupation:
        params["filterByOccupation"] = filter_by_occupation
    if filter_by_headline:
        params["filterByHeadline"] = filter_by_headline
    if filter_by_out_of_office is not None:
        params["filterByOutOfOffice"] = str(filter_by_out_of_office).lower()
    if filter_by_step_change_timestamp:
        params["filterByStepChangeTimestamp"] = filter_by_step_change_timestamp
    if filter_by_selected_leads:
        params["filterBySelectedLeads"] = (
            f"[{','.join(map(str, filter_by_selected_leads))}]"
        )

    result = await client.request(
        "GET", f"/users/{user_id}/accounts/{account_id}/leads", params=params
    )
    return result


# ============================================================================
# CAMPAIGNS TOOLS - All endpoints (6 new tools)
# ============================================================================


@mcp.tool()
async def export_all_campaigns(user_id: str, account_id: str) -> Dict[str, Any]:
    """
    Export all campaigns in CSV format

    Args:
        user_id: The ID of the user
        account_id: The ID of the account (seat)

    Returns:
        CSV export of all campaigns or download URL
    """
    result = await client.request(
        "POST", f"/users/{user_id}/accounts/{account_id}/campaigns/export"
    )
    return result


@mcp.tool()
async def export_leads_from_campaign(
    user_id: str,
    account_id: str,
    campaign_id: str,
    search: Optional[str] = None,
    filter_by_verified_emails: Optional[bool] = None,
    filter_by_not_verified_emails: Optional[bool] = None,
    filter_by_status: Optional[List[int]] = None,
    filter_by_connection_degree: Optional[List[int]] = None,
    filter_by_current_step: Optional[List[int]] = None,
    filter_by_selected_leads: Optional[List[int]] = None,
    filter_by_name: Optional[str] = None,
    filter_by_company: Optional[str] = None,
    filter_by_occupation: Optional[str] = None,
    filter_by_headline: Optional[str] = None,
    filter_by_out_of_office: Optional[bool] = None,
    filter_by_step_change_timestamp: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Export leads from a specific campaign in CSV format with advanced filtering

    Supports 7 groups of filters with OR logic within groups and AND logic between groups.

    Args:
        user_id: The ID of the user
        account_id: The ID of the account (seat)
        campaign_id: The ID of the campaign to export leads from
        search: Search leads by fullName, email, company, headline, etc.
        filter_by_verified_emails: Export leads with verified emails
        filter_by_not_verified_emails: Export leads without verified emails
        filter_by_status: Filter by status ([1]=Discovered, [2]=Connection pending,
            [3]=Connected not replied, [4]=Replied)
        filter_by_connection_degree: Used with filter_by_status=[4] for additional
            status filtering
        filter_by_current_step: Export leads on specific campaign steps
        filter_by_selected_leads: Export specific leads by their IDs
        filter_by_name: Export leads whose names contain this value
        filter_by_company: Export leads whose company contains this value
        filter_by_occupation: Export leads whose occupation contains this value
        filter_by_headline: Export leads whose headline contains this value
        filter_by_out_of_office: Export leads with "Out of office" status
        filter_by_step_change_timestamp: Export leads with stepChangeTimestamp greater than this

    Returns:
        CSV export data or download URL

    Example:
        export_leads_from_campaign(
            user_id="123",
            account_id="456",
            campaign_id="789",
            filter_by_status=[4],
            filter_by_verified_emails=True
        )
    """
    params: Dict[str, Any] = {}

    if search:
        params["search"] = search
    if filter_by_verified_emails is not None:
        params["filterByVerifiedEmails"] = str(filter_by_verified_emails).lower()
    if filter_by_not_verified_emails is not None:
        params["filterByNotVerifiedEmails"] = str(filter_by_not_verified_emails).lower()
    if filter_by_status:
        params["filterByStatus"] = f"[{','.join(map(str, filter_by_status))}]"
    if filter_by_connection_degree:
        params["filterByConnectionDegree"] = (
            f"[{','.join(map(str, filter_by_connection_degree))}]"
        )
    if filter_by_current_step:
        params["filterByCurrentStep"] = (
            f"[{','.join(map(str, filter_by_current_step))}]"
        )
    if filter_by_selected_leads:
        params["filterBySelectedLeads"] = (
            f"[{','.join(map(str, filter_by_selected_leads))}]"
        )
    if filter_by_name:
        params["filterByName"] = filter_by_name
    if filter_by_company:
        params["filterByCompany"] = filter_by_company
    if filter_by_occupation:
        params["filterByOccupation"] = filter_by_occupation
    if filter_by_headline:
        params["filterByHeadline"] = filter_by_headline
    if filter_by_out_of_office is not None:
        params["filterByOutOfOffice"] = str(filter_by_out_of_office).lower()
    if filter_by_step_change_timestamp:
        params["filterByStepChangeTimestamp"] = filter_by_step_change_timestamp

    result = await client.request(
        "GET",
        f"/users/{user_id}/accounts/{account_id}/campaigns/{campaign_id}/export",
        params=params,
    )
    return result


@mcp.tool()
async def get_campaign_info(
    user_id: str, account_id: str, campaign_id: str
) -> Dict[str, Any]:
    """
    Retrieve detailed information about a specific campaign

    Args:
        user_id: The ID of the user
        account_id: The ID of the account (seat)
        campaign_id: The ID of the campaign

    Returns:
        Campaign details including name, status, steps, statistics, etc.
    """
    result = await client.request(
        "GET",
        f"/users/{user_id}/accounts/{account_id}/campaigns/{campaign_id}/details",
    )
    return result


@mcp.tool()
async def get_campaign_list(
    user_id: str,
    account_id: str,
    campaign_state: Optional[int] = 1,
    sort_order: Optional[str] = None,
    sort_column: Optional[str] = None,
    limit: int = 30,
    offset: int = 0,
) -> Dict[str, Any]:
    """
    Retrieve list of all campaigns with filtering and sorting

    Args:
        user_id: The ID of the user
        account_id: The ID of the account (seat)
        campaign_state: Campaign status filter (1=ACTIVE, 2=DRAFT, 3=ARCHIVED, default: 1)
        sort_order: Sort direction ("ASC" or "DESC")
        sort_column: Column to sort by ("isActive", "name", or "createdAt")
        limit: Number of results to return (default: 30)
        offset: Pagination offset (default: 0)

    Returns:
        List of campaigns with pagination metadata

    Example:
        get_campaign_list(
            user_id="123",
            account_id="456",
            campaign_state=1,
            sort_order="DESC",
            sort_column="createdAt",
            limit=50
        )
    """
    params: Dict[str, Any] = {"limit": limit, "offset": offset}

    if campaign_state is not None:
        params["campaignState"] = campaign_state
    if sort_order:
        params["sortOrder"] = sort_order
    if sort_column:
        params["sortColumn"] = sort_column

    result = await client.request(
        "GET", f"/users/{user_id}/accounts/{account_id}/campaigns", params=params
    )
    return result


@mcp.tool()
async def create_lead_source(
    user_id: str,
    account_id: str,
    campaign_id: int,
    lead_source_url: str,
    lead_source_type: str,
    dashboard: Optional[int] = None,
    auto_reuse: Optional[int] = None,
    auto_reuse_interval: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Create a lead source and link it to a campaign

    This creates a lead source (e.g., Sales Navigator search URL) and connects it
    to a campaign for automatic lead import.

    Args:
        user_id: The ID of the user who owns the seat
        account_id: The ID of the seat where the campaign is located
        campaign_id: The ID of the campaign to link the lead source to
        lead_source_url: URL of the lead source (e.g., LinkedIn Sales Navigator search)
        lead_source_type: Type of lead source (e.g., "SALES_NAVIGATOR")
        dashboard: Dashboard ID (optional)
        auto_reuse: Auto-reuse setting (optional, 1 to enable)
        auto_reuse_interval: Auto-reuse interval in days (optional)

    Returns:
        Created lead source information

    Example:
        create_lead_source(
            user_id="123",
            account_id="456",
            campaign_id=789,
            lead_source_url="https://www.linkedin.com/sales/search/people?...",
            lead_source_type="SALES_NAVIGATOR",
            dashboard=2,
            auto_reuse=1,
            auto_reuse_interval=100
        )
    """
    lead_source = {
        "campaignId": campaign_id,
        "leadSourceUrl": lead_source_url,
        "leadSourceType": lead_source_type,
    }

    if dashboard is not None:
        lead_source["dashboard"] = dashboard
    if auto_reuse is not None:
        lead_source["autoReuse"] = auto_reuse
    if auto_reuse_interval is not None:
        lead_source["autoReuseInterval"] = auto_reuse_interval

    request_data = {"leadSources": [lead_source]}

    result = await client.request(
        "POST",
        f"/users/{user_id}/accounts/{account_id}/lead_sources",
        json_data=request_data,
    )
    return result


@mcp.tool()
async def create_campaign_from_template(
    user_id: str,
    account_id: str,
    sequence_template_id: str,
    campaign_name: str,
    lead_source_url: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create a new campaign from a saved sequence template

    This creates a URL-based campaign from the user's saved sequences.
    The campaign goes live immediately after creation.

    Args:
        user_id: The ID of the user
        account_id: The ID of the account (seat)
        sequence_template_id: The ID of the sequence template to use
        campaign_name: Name for the new campaign
        lead_source_url: Optional lead source URL to attach to the campaign

    Returns:
        Created campaign information

    Example:
        create_campaign_from_template(
            user_id="123",
            account_id="456",
            sequence_template_id="789",
            campaign_name="Q1 Outreach Campaign",
            lead_source_url="https://linkedin.com/sales/search/..."
        )
    """
    campaign_data = {
        "sequenceTemplateId": sequence_template_id,
        "name": campaign_name,
    }

    if lead_source_url:
        campaign_data["leadSourceUrl"] = lead_source_url

    result = await client.request(
        "POST",
        f"/users/{user_id}/accounts/{account_id}/campaigns",
        json_data=campaign_data,
    )
    return result


# STATISTICS TOOLS (4 endpoints)
# ============================================================================


@mcp.tool()
async def get_statistics(
    user_id: str,
    account_id: str,
    from_timestamp: int,
    to_timestamp: int,
    curves: List[int],
    time_zone: str,
    campaign_id: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Get statistics for campaigns within a time range

    This retrieves statistics for all campaigns or a specific campaign if campaign_id is provided.

    Args:
        user_id: User ID
        account_id: Account ID
        from_timestamp: Statistics start timestamp (Unix timestamp)
        to_timestamp: Statistics end timestamp (Unix timestamp)
        curves: List of statistic types to retrieve. Values:
            1=PROFILE_VIEW, 2=PROFILE_FOLLOW, 3=INVITATION_SENT, 4=MESSAGE_SENT,
            5=INMAIL_SENT, 10=EMAIL_SENT, 11=EMAIL_OPENED, 12=EMAIL_CLICKED,
            16=EMAIL_VERIFIED, 6=INVITATION_ACCEPTED, 7=MESSAGE_REPLY,
            8=INVITATION_ACCEPTED_RATE, 9=MESSAGE_REPLY_RATE, 14=EMAIL_OPEN_RATE,
            15=EMAIL_CLICK_RATE, 17=EMAIL_BOUNCE_RATE
        time_zone: Timezone for statistics (e.g., "America/New_York", "Europe/Belgrade")
        campaign_id: Optional campaign ID to get statistics for a specific campaign

    Returns:
        Campaign statistics data
    """
    params = {
        "from": from_timestamp,
        "to": to_timestamp,
        "curves": curves,
        "timeZone": time_zone,
    }

    if campaign_id is not None:
        params["campaignId"] = campaign_id

    result = await client.request(
        "GET", f"/users/{user_id}/accounts/{account_id}/statistics", params=params
    )
    return result


@mcp.tool()
async def export_statistics_csv(
    user_id: str,
    account_id: str,
    from_timestamp: int,
    to_timestamp: int,
    curves: List[int],
    time_zone: str,
) -> Dict[str, Any]:
    """
    Export campaign statistics as a CSV file

    This retrieves statistics for all campaigns in CSV format.

    Args:
        user_id: User ID
        account_id: Account ID
        from_timestamp: Statistics start timestamp (Unix timestamp)
        to_timestamp: Statistics end timestamp (Unix timestamp)
        curves: List of statistic types to retrieve (same values as get_statistics)
        time_zone: Timezone for statistics (e.g., "America/New_York", "Europe/Belgrade")

    Returns:
        CSV file data with campaign statistics
    """
    params = {
        "from": from_timestamp,
        "to": to_timestamp,
        "curves": curves,
        "timeZone": time_zone,
    }

    result = await client.request(
        "GET", f"/users/{user_id}/accounts/{account_id}/statistics/export_csv", params=params
    )
    return result


@mcp.tool()
async def get_step_statistics(
    user_id: str,
    account_id: str,
    campaign_id: int,
) -> Dict[str, Any]:
    """
    Get step statistics for a specific campaign

    This retrieves statistics for individual campaign steps within a specific campaign.

    Args:
        user_id: User ID
        account_id: Account ID
        campaign_id: Campaign ID to get step statistics for

    Returns:
        Step-by-step statistics for the campaign
    """
    params = {"campaignId": campaign_id}

    result = await client.request(
        "GET", f"/users/{user_id}/accounts/{account_id}/statistics/steps", params=params
    )
    return result


@mcp.tool()
async def get_all_campaigns_statistics(
    user_id: str,
    account_id: str,
    campaign_state: Optional[int] = 1,
) -> Dict[str, Any]:
    """
    Get summary statistics for all campaigns

    This retrieves platform-wide summary statistics (totals) for all campaigns.

    Args:
        user_id: User ID
        account_id: Account ID
        campaign_state: Optional campaign state filter (default: 1)

    Returns:
        Summary statistics for all campaigns
    """
    params = {}
    if campaign_state is not None:
        params["campaignState"] = campaign_state

    result = await client.request(
        "GET",
        f"/users/{user_id}/accounts/{account_id}/all_campaigns_statistics",
        params=params,
    )
    return result


# ============================================================================
# BLACKLIST TOOLS (4 endpoints)
# ============================================================================


@mcp.tool()
async def add_keywords_to_global_blacklist(
    team_id: str,
    user_id: str,
    keywords: List[str],
    keyword_type: str,
    comparison_type: str,
) -> Dict[str, Any]:
    """
    Add keywords to the global blacklist via JSON

    Args:
        team_id: Team ID
        user_id: User ID
        keywords: List of keywords to blacklist (e.g., ["test", "test123"])
        keyword_type: Type of keyword. Options: "company_name", "email", "domain",
            "full_name", "profile_url", "job_title"
        comparison_type: How to match keywords. Options: "exact", "contains",
            "starts_with", "ends_with"

    Returns:
        Success confirmation
    """
    # Note: API expects formdata, but we'll send as JSON with proper structure
    form_data = {
        "keywords": keywords,
        "type": keyword_type,
        "comparisonType": comparison_type,
        "source": "manual",
    }

    result = await client.request(
        "PATCH",
        f"/teams/{team_id}/users/{user_id}/global_blacklists/add_keyword",
        json_data=form_data,
    )
    return result


@mcp.tool()
async def import_keywords_to_global_blacklist_csv(
    team_id: str,
    user_id: str,
    csv_file_path: str,
    keyword_type: str,
    comparison_type: str,
) -> Dict[str, Any]:
    """
    Import keywords to global blacklist from a CSV file

    Args:
        team_id: Team ID
        user_id: User ID
        csv_file_path: Path to CSV file containing keywords
        keyword_type: Type of keyword. Options: "company_name", "email", "domain",
            "full_name", "profile_url", "job_title"
        comparison_type: How to match keywords. Options: "exact", "contains",
            "starts_with", "ends_with"

    Returns:
        Success confirmation with import results
    """
    # Note: This endpoint requires multipart/form-data file upload
    # For now, we'll return an error with instructions
    raise ToolError(
        "CSV file upload is not yet implemented in this MCP server. "
        "Please use the add_keywords_to_global_blacklist tool with a list of keywords instead, "
        "or upload the CSV file directly via the Multilead web interface."
    )


@mcp.tool()
async def add_keywords_to_blacklist(
    user_id: str,
    account_id: str,
    keywords: List[str],
    keyword_type: str,
    comparison_type: str,
) -> Dict[str, Any]:
    """
    Add keywords to your seat's blacklist via JSON

    Args:
        user_id: User ID
        account_id: Account ID (seat ID)
        keywords: List of keywords to blacklist (e.g., ["John Smith"])
        keyword_type: Type of keyword. Options: "company_name", "email", "domain",
            "full_name", "profile_url", "job_title"
        comparison_type: How to match keywords. Options: "exact", "contains",
            "starts_with", "ends_with"

    Returns:
        Success confirmation
    """
    blacklist_data = {
        "keywords": keywords,
        "type": keyword_type,
        "comparisonType": comparison_type,
        "source": "manual",
    }

    result = await client.request(
        "PATCH",
        f"/users/{user_id}/accounts/{account_id}/blacklists/add_keyword",
        json_data=blacklist_data,
    )
    return result


@mcp.tool()
async def import_keywords_to_blacklist_csv(
    user_id: str,
    account_id: str,
    csv_file_path: str,
    keyword_type: str,
    comparison_type: str,
) -> Dict[str, Any]:
    """
    Import keywords to your seat's blacklist from a CSV file

    Args:
        user_id: User ID
        account_id: Account ID (seat ID)
        csv_file_path: Path to CSV file containing keywords
        keyword_type: Type of keyword. Options: "company_name", "email", "domain",
            "full_name", "profile_url", "job_title"
        comparison_type: How to match keywords. Options: "exact", "contains",
            "starts_with", "ends_with"

    Returns:
        Success confirmation with import results
    """
    # Note: This endpoint requires multipart/form-data file upload
    # For now, we'll return an error with instructions
    raise ToolError(
        "CSV file upload is not yet implemented in this MCP server. "
        "Please use the add_keywords_to_blacklist tool with a list of keywords instead, "
        "or upload the CSV file directly via the Multilead web interface."
    )


# ============================================================================
# WARMUP TOOLS (1 endpoint)
# ============================================================================


@mcp.tool()
async def activate_inboxflare_warmup(user_id: str) -> Dict[str, Any]:
    """
    Activate InboxFlare warm-up for a user

    This endpoint creates an account for the user on the InboxFlare warm-up tool
    and sends credentials via email.

    Args:
        user_id: User ID to activate warm-up for

    Returns:
        Success confirmation with account creation details
    """
    result = await client.request("POST", f"/users/{user_id}/activate_warmup_inboxflare")
    return result


# ============================================================================
# USERS & SEATS TOOLS (18 endpoints)
# ============================================================================


@mcp.tool()
async def list_all_seats_of_a_specific_user(
    search: Optional[str] = None
) -> Dict[str, Any]:
    """
    List All Seats of a Specific User

    This action provides information based on your Team Management role:
    - For team members: Retrieves information about the seats you've been invited to manage or own
    - For co-workers: Retrieves information about the seats that belong to the teams you manage
    - For platform admins: Retrieves information about the seats linked to the teams you own

    Args:
        search: Optional search query to filter seats (e.g., "John Smith")

    Returns:
        List of seats with detailed information
    """
    params = {}
    if search is not None:
        params["search"] = search

    result = await client.request("GET", "/accounts", params=params)
    return result


@mcp.tool()
async def register_new_user(
    email: str,
    password: str,
    full_name: str,
    whitelabel_id: int,
    phone: Optional[str] = None,
    invitation_id: Optional[str] = None,
    skip_confirmation_email: Optional[bool] = None,
) -> Dict[str, Any]:
    """
    Register New User

    This action registers a new user on the platform.

    Args:
        email: User's email address (required)
        password: User's password (required)
        full_name: User's full display name (required)
        whitelabel_id: Whitelabel ID (required)
        phone: Optional phone number (e.g., "+3816423416")
        invitation_id: Optional invitation ID for secure registration
        skip_confirmation_email: Set to True to skip confirmation email (default: False)

    Returns:
        Created user object with registration details
    """
    request_data = {
        "email": email,
        "password": password,
        "fullName": full_name,
        "whitelabelId": whitelabel_id,
    }

    if phone is not None:
        request_data["phone"] = phone
    if invitation_id is not None:
        request_data["invitationId"] = invitation_id
    if skip_confirmation_email is not None:
        request_data["skipConfirmationEmail"] = skip_confirmation_email

    result = await client.request("POST", "/users/register", json_data=request_data)
    return result


@mcp.tool()
async def get_user_information() -> Dict[str, Any]:
    """
    Get User Information

    This action retrieves all information on the authorized user (the user whose
    API key is being used).

    Returns:
        Complete user information including profile, settings, and permissions
    """
    result = await client.request("GET", "/user/me")
    return result


@mcp.tool()
async def list_all_users_as_a_whitelabel(
    limit: Optional[int] = None,
    offset: Optional[int] = None,
) -> Dict[str, Any]:
    """
    List All Users as a Whitelabel

    As a whitelabel, this action retrieves the list of all your users.

    Args:
        limit: Maximum number of results to retrieve (default: 30)
        offset: Position in the dataset to start from (default: 0)

    Returns:
        Paginated list of users with metadata
    """
    params = {}
    if limit is not None:
        params["limit"] = limit
    if offset is not None:
        params["offset"] = offset

    result = await client.request("GET", "/users", params=params)
    return result


@mcp.tool()
async def create_seat(
    user_id: str,
    plan_id: int,
    full_name: str,
    start_utc_time: str,
    end_utc_time: str,
    time_zone: str,
    team_id: int,
    whitelabel_id: int,
) -> Dict[str, Any]:
    """
    Create Seat

    This action creates a new seat within a specific team.

    Args:
        user_id: User ID who owns the seat
        plan_id: Plan ID for the seat subscription
        full_name: Full name for the seat
        start_utc_time: Start time in UTC (e.g., "08:00")
        end_utc_time: End time in UTC (e.g., "16:00")
        time_zone: Timezone (e.g., "Europe/Belgrade", "America/New_York")
        team_id: Team ID to create the seat in
        whitelabel_id: Whitelabel ID

    Returns:
        Created seat object with subscription details
    """
    request_data = {
        "planId": plan_id,
        "fullName": full_name,
        "startUTCTime": start_utc_time,
        "endUTCTime": end_utc_time,
        "timeZone": time_zone,
        "teamId": team_id,
        "whitelabelId": whitelabel_id,
    }

    result = await client.request(
        "POST", f"/users/{user_id}/accounts/register", json_data=request_data
    )
    return result


@mcp.tool()
async def cancel_seat(
    user_id: str,
    account_id: str,
    reason: str,
) -> Dict[str, Any]:
    """
    Cancel Seat

    This action cancels a specific seat within a specific team.

    Args:
        user_id: User ID who owns the seat
        account_id: Account/Seat ID to cancel
        reason: Reason for cancellation

    Returns:
        Cancellation confirmation with details
    """
    request_data = {"reason": reason}

    result = await client.request(
        "POST",
        f"/users/{user_id}/subscriptions/accounts/{account_id}",
        json_data=request_data,
    )
    return result


@mcp.tool()
async def reactivate_seat(
    user_id: str,
    account_id: str,
    proxy_country: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Reactivate Seat

    This action reactivates a specific inactive seat within a specific team.

    Args:
        user_id: User ID who owns the seat
        account_id: Account/Seat ID to reactivate
        proxy_country: Optional proxy country code (e.g., "us", "gb")

    Returns:
        Reactivation confirmation with updated seat status
    """
    request_data = {}
    if proxy_country is not None:
        request_data["proxyCountry"] = proxy_country

    result = await client.request(
        "PUT",
        f"/users/{user_id}/accounts/{account_id}/reactivate",
        json_data=request_data,
    )
    return result


@mcp.tool()
async def suspend_or_unsuspend_seat(
    user_id: str,
    account_id: int,
    suspended: bool,
) -> Dict[str, Any]:
    """
    Suspend or Unsuspend Seat

    This action suspends or unsuspends a specific seat within a specific team.

    Args:
        user_id: User ID who owns the seat
        account_id: Account/Seat ID to suspend/unsuspend
        suspended: True to suspend, False to unsuspend

    Returns:
        Updated seat status
    """
    request_data = {
        "accountId": account_id,
        "suspended": suspended,
    }

    result = await client.request(
        "PUT", f"/users/{user_id}/accounts/suspend", json_data=request_data
    )
    return result


@mcp.tool()
async def resend_email_confirmation_message(
    user_id: str,
    email: str,
) -> Dict[str, Any]:
    """
    Resend Email Confirmation Message

    This action resends an email confirmation message to the user's email and allows
    them to confirm their email address.

    Args:
        user_id: User ID to resend confirmation for
        email: Email address that should receive the confirmation email

    Returns:
        Confirmation that the email was sent
    """
    # This endpoint uses form-data
    request_data = {"email": email}

    result = await client.request(
        "POST", f"/users/{user_id}/resend_confirmation", json_data=request_data
    )
    return result


@mcp.tool()
async def send_password_reset_email(email: str) -> Dict[str, Any]:
    """
    Send Password Reset Email

    This action initializes the user's password reset and sends a password reset email.

    Args:
        email: Email address to receive the password reset link

    Returns:
        Confirmation that the reset email was sent
    """
    # This endpoint uses form-data
    request_data = {"email": email}

    result = await client.request(
        "POST", "/users/reset_password_email", json_data=request_data
    )
    return result


@mcp.tool()
async def list_users_associated_with_a_specific_seat(
    user_id: str,
    account_id: str,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    search: Optional[str] = None,
) -> Dict[str, Any]:
    """
    List Users Associated With a Specific Seat

    This action retrieves all users associated with the chosen seat in any way.
    The way they are related to a seat determines their user types:
    1. Team Member: Users invited to the team and assigned a seat
    2. Coworker: Users who manage a team that owns the seat
    3. Platform Admin: Users who manage the platform containing the seat

    Args:
        user_id: User ID
        account_id: Account/Seat ID
        limit: Maximum number of results (default: 30)
        offset: Starting position in dataset (default: 0)
        search: Search query for email or fullName

    Returns:
        Paginated list of associated users with their roles
    """
    params = {}
    if limit is not None:
        params["limit"] = limit
    if offset is not None:
        params["offset"] = offset
    if search is not None:
        params["search"] = search

    result = await client.request(
        "GET",
        f"/users/{user_id}/accounts/{account_id}/get_associated_users",
        params=params,
    )
    return result


@mcp.tool()
async def list_teams_under_the_users_white_label(user_id: str) -> Dict[str, Any]:
    """
    List Teams Under the User's White Label

    This action retrieves all teams under one platform (White label).
    The user who runs this endpoint must be the platform admin.

    Args:
        user_id: User ID (must be platform admin)

    Returns:
        List of all teams under the whitelabel
    """
    result = await client.request("GET", f"/users/{user_id}/teams")
    return result


@mcp.tool()
async def change_a_password(
    user_id: str,
    new_password: str,
) -> Dict[str, Any]:
    """
    Change A Password

    This action changes the password for a specific user. Regular users can only
    change their own password and platform co-owners can change the password for
    all users within their platform.

    Args:
        user_id: User ID whose password to change
        new_password: New password to set

    Returns:
        Confirmation of password change
    """
    request_data = {"newPassword": new_password}

    result = await client.request(
        "POST", f"/users/{user_id}/change_password", json_data=request_data
    )
    return result


@mcp.tool()
async def get_users_sequence_templates(
    user_id: str,
    team_id: str,
) -> Dict[str, Any]:
    """
    Get User's Sequence Templates

    This action retrieves all sequence templates (saved sequences) from a user who
    is a part of certain team. You can use the returned sequence template IDs in
    the "Create Campaign From A Sequence Template" endpoint.

    Args:
        user_id: ID of the user whose saved sequences to retrieve
        team_id: ID of the team that the user is part of

    Returns:
        List of saved sequence templates with IDs
    """
    result = await client.request(
        "GET", f"/users/{user_id}/teams/{team_id}/saved_sequences"
    )
    return result


@mcp.tool()
async def transfer_credits(
    user_id: str,
    destination_user_id: int,
    quantity: int,
) -> Dict[str, Any]:
    """
    Transfer Credits

    This action transfers credits from the authenticated user to a specified
    destination user.

    Args:
        user_id: Source user ID (authenticated user)
        destination_user_id: Destination user ID to receive credits
        quantity: Number of credits to transfer

    Returns:
        Transfer confirmation with updated credit balances
    """
    request_data = {
        "destinationUserId": destination_user_id,
        "quantity": quantity,
    }

    result = await client.request(
        "POST", f"/api/open-api/v2/users/{user_id}/transfer_credits", json_data=request_data
    )
    return result


@mcp.tool()
async def connect_linkedin_account(
    user_id: str,
    account_id: str,
    linkedin_email: str,
    linkedin_password: str,
    linkedin_subscription_id: int,
    country_code: str,
    setup_proxy_type: str,
    note: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Connect LinkedIn Account

    This actions connects a specific LinkedIn account to a specific seat.

    Args:
        user_id: User ID
        account_id: Account/Seat ID
        linkedin_email: LinkedIn account email
        linkedin_password: LinkedIn account password
        linkedin_subscription_id: LinkedIn subscription type ID
        country_code: Country code for proxy (e.g., "us", "gb")
        setup_proxy_type: Proxy setup type (e.g., "BUY")
        note: Optional note about the connection

    Returns:
        LinkedIn connection status and details
    """
    request_data = {
        "linkedinEmail": linkedin_email,
        "linkedinPassword": linkedin_password,
        "linkedinSubscriptionId": linkedin_subscription_id,
        "countryCode": country_code,
        "setupProxyType": setup_proxy_type,
    }

    if note is not None:
        request_data["note"] = note

    result = await client.request(
        "POST",
        f"/users/{user_id}/accounts/{account_id}/connect_linkedin",
        json_data=request_data,
    )
    return result


@mcp.tool()
async def disconnect_linkedin_account(
    user_id: str,
    account_id: str,
) -> Dict[str, Any]:
    """
    Disconnect LinkedIn Account

    This action disconnects a specific LinkedIn account from the seat on the platform.

    Args:
        user_id: User ID
        account_id: Account/Seat ID with LinkedIn connection

    Returns:
        Disconnection confirmation
    """
    result = await client.request(
        "PATCH", f"/users/{user_id}/accounts/{account_id}/disconnect_linkedin"
    )
    return result




# ============================================================================
# TEAM MANAGEMENT TOOLS (6 endpoints)
# ============================================================================


@mcp.tool()
async def create_team(user_id: str, name: str) -> Dict[str, Any]:
    """
    Create a new team for a specific user

    Args:
        user_id: The user ID who will own the team (required)
        name: The name of the team to create (required)

    Returns:
        Created team object with ID and metadata

    Example:
        create_team(user_id="1451", name="Sales Team")
    """
    team_data = {"name": name}

    result = await client.request(
        "POST", f"/users/{user_id}/create_team", json_data=team_data
    )
    return result


@mcp.tool()
async def create_team_role(
    team_id: str,
    user_id: str,
    name: str,
    permissions: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Create a role for a specific team with custom permissions

    Args:
        team_id: The ID of the team for which to create this role (required)
        user_id: Your user ID (required)
        name: The name of the role (required)
        permissions: List of permission objects with 'id' and 'isViewOnly' fields (required)

    Returns:
        Created role object with ID and permissions

    Example:
        create_team_role(
            team_id="1570",
            user_id="1451",
            name="Manager",
            permissions=[
                {"id": 1, "isViewOnly": False},
                {"id": 2, "isViewOnly": False}
            ]
        )
    """
    role_data = {"name": name, "permissions": permissions}

    result = await client.request(
        "POST", f"/teams/{team_id}/users/{user_id}/create_role", json_data=role_data
    )
    return result


@mcp.tool()
async def get_team_roles(team_id: str, user_id: str) -> Dict[str, Any]:
    """
    Retrieve all roles for a specific team

    Args:
        team_id: The ID of the team for which to retrieve roles (required)
        user_id: Your user ID (required)

    Returns:
        List of all roles configured for the team with their permissions

    Example:
        get_team_roles(team_id="1", user_id="1451")
    """
    result = await client.request("GET", f"/teams/{team_id}/users/{user_id}/get_roles")
    return result


@mcp.tool()
async def get_team_members(user_id: str, team_id: str) -> Dict[str, Any]:
    """
    Retrieve all members from a specific team

    Args:
        user_id: Your user ID (required)
        team_id: The ID of the team for which to retrieve members (required)

    Returns:
        List of all team members with their roles and permissions

    Example:
        get_team_members(user_id="1451", team_id="1443")
    """
    result = await client.request(
        "GET", f"/users/{user_id}/teams/{team_id}/get_team_members"
    )
    return result


@mcp.tool()
async def invite_team_member(
    team_id: str,
    user_id: str,
    name: str,
    email: str,
    account_roles: List[Dict[str, Any]],
    can_manage_payment: bool = False,
    send_invitation_email: bool = False,
) -> Dict[str, Any]:
    """
    Invite a user to become a member of a specific team

    The sendAnInvitationEmail flag controls how the invitation works:
    - If False (default): No email is sent and the invitation is automatically accepted
    - If True: An email invitation is sent and the user can accept or decline

    Args:
        team_id: The ID of the team to invite the member to (required)
        user_id: Your user ID (required)
        name: The name of the user to invite (required)
        email: The email address of the user to invite (required)
        account_roles: List of role assignments with 'roleId' and 'accounts' array (required)
        can_manage_payment: Whether the user can manage payment settings (default: False)
        send_invitation_email: Whether to send an email invitation (default: False)

    Returns:
        Invitation object with member details and status

    Example:
        invite_team_member(
            team_id="1443",
            user_id="1451",
            name="John Doe",
            email="john@company.com",
            account_roles=[
                {
                    "roleId": "6eb0c288-0a17-4f6c-88a3-bb750b34d7ca",
                    "accounts": [1028]
                }
            ],
            can_manage_payment=False,
            send_invitation_email=True
        )
    """
    invitation_data = {
        "name": name,
        "email": email,
        "accountRoles": account_roles,
        "canManagePayment": can_manage_payment,
        "sendAnInvitationEmail": send_invitation_email,
    }

    result = await client.request(
        "POST",
        f"/teams/{team_id}/users/{user_id}/invite_team_member",
        json_data=invitation_data,
    )
    return result


@mcp.tool()
async def update_team_member(
    team_id: str,
    user_id: str,
    email: str,
    account_roles: Optional[List[Dict[str, Any]]] = None,
    can_manage_team_global_webhooks: Optional[bool] = None,
) -> Dict[str, Any]:
    """
    Edit and update a team member from a specific team

    Args:
        team_id: The ID of the team this member is part of (required)
        user_id: Your user ID (required)
        email: The email address of the member to update (required)
        account_roles: Updated list of role assignments with 'roleId' and 'accounts' array
        can_manage_team_global_webhooks: Whether the user can manage team global webhooks

    Returns:
        Updated team member object with new settings

    Example:
        update_team_member(
            team_id="1443",
            user_id="1451",
            email="borisa@company.io",
            account_roles=[
                {
                    "roleId": "d144079f-2a22-4f86-b2a9-45b3289b4bf4",
                    "accounts": [158]
                }
            ],
            can_manage_team_global_webhooks=True
        )
    """
    update_data = {"email": email}

    if account_roles is not None:
        update_data["accountRoles"] = account_roles

    if can_manage_team_global_webhooks is not None:
        update_data["canManageTeamGlobalWebhooks"] = can_manage_team_global_webhooks

    result = await client.request(
        "PATCH",
        f"/teams/{team_id}/users/{user_id}/update_team_member",
        json_data=update_data,
    )
    return result


# ============================================================================
# SETTINGS TOOLS (1 endpoint)
# ============================================================================


@mcp.tool()
async def sync_linkedin_messages(user_id: str, account_id: str) -> Dict[str, Any]:
    """
    Sync all LinkedIn messages for a specific seat to the platform inbox

    This action retrieves all LinkedIn messages for a specific seat and displays them
    inside the platform's inbox for centralized message management.

    Args:
        user_id: Your user ID (required)
        account_id: The ID of the seat for which to sync LinkedIn messages (required)

    Returns:
        Sync status and count of messages retrieved

    Example:
        sync_linkedin_messages(user_id="16911", account_id="9852")
    """
    result = await client.request(
        "GET", f"/users/{user_id}/accounts/{account_id}/fetch_conversations"
    )
    return result



# ============================================================================
# CONVERSATIONS & MESSAGES TOOLS (12 endpoints)
# ============================================================================


@mcp.tool()
async def get_messages_from_a_specific_thread(
    user_id: str,
    account_id: str,
    threads: List[str],
    filter_by_step_change_timestamp: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Retrieve messages from specific conversation threads

    This retrieves messages from one or more specific threads, with optional filtering
    by step change timestamp to get only recent updates.

    Args:
        user_id: User ID
        account_id: Account ID
        threads: List of thread IDs to retrieve messages from
        filter_by_step_change_timestamp: Optional ISO timestamp to filter messages
            that were updated after this time

    Returns:
        Messages from the specified threads
    """
    params = {}
    if threads:
        params["threads"] = json.dumps(threads)
    if filter_by_step_change_timestamp is not None:
        params["filterByStepChangeTimestamp"] = filter_by_step_change_timestamp

    result = await client.request(
        "GET",
        f"/users/{user_id}/accounts/{account_id}/conversations/threads",
        params=params,
    )
    return result


@mcp.tool()
async def get_conversations_by_identifiers(
    user_id: str,
    account_id: str,
    identifiers: List[str],
) -> Dict[str, Any]:
    """
    Retrieve conversations using specific identifiers

    This finds all conversations associated with the provided identifiers
    (e.g., LinkedIn profile IDs, email addresses).

    Args:
        user_id: User ID
        account_id: Account ID
        identifiers: List of identifiers to search for (e.g., LinkedIn IDs)

    Returns:
        Conversations matching the provided identifiers
    """
    params = {}
    if identifiers:
        params["identifiers"] = json.dumps(identifiers)

    result = await client.request(
        "GET",
        f"/users/{user_id}/accounts/{account_id}/conversations/identifiers",
        params=params,
    )
    return result


@mcp.tool()
async def get_unread_conversations(
    user_id: str,
    account_id: str,
    limit: int = 100,
    offset: int = 0,
    name: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Retrieve unread conversations

    This gets all conversations that have not been marked as read, with optional
    filtering by contact name.

    Args:
        user_id: User ID
        account_id: Account ID
        limit: Maximum number of results to return (default: 100)
        offset: Pagination offset (default: 0)
        name: Optional search filter for contact name

    Returns:
        List of unread conversations
    """
    params = {}
    if limit is not None:
        params["limit"] = limit
    if offset is not None:
        params["offset"] = offset
    if name is not None:
        params["name"] = name

    result = await client.request(
        "GET",
        f"/users/{user_id}/accounts/{account_id}/conversations/unread",
        params=params,
    )
    return result


@mcp.tool()
async def get_other_conversations(
    user_id: str,
    account_id: str,
    limit: int = 100,
    offset: int = 0,
    name: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Retrieve other conversations (not categorized as unread)

    This gets conversations from the "All other messages" section.

    Args:
        user_id: User ID
        account_id: Account ID
        limit: Maximum number of results to return (default: 100)
        offset: Pagination offset (default: 0)
        name: Optional search filter for contact name

    Returns:
        List of other conversations
    """
    params = {}
    if limit is not None:
        params["limit"] = limit
    if offset is not None:
        params["offset"] = offset
    if name is not None:
        params["name"] = name

    result = await client.request(
        "GET",
        f"/users/{user_id}/accounts/{account_id}/conversations/other",
        params=params,
    )
    return result


@mcp.tool()
async def get_all_conversations(
    user_id: str,
    account_id: str,
    limit: int = 100,
    offset: int = 0,
    name: Optional[str] = None,
    tag_ids: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Retrieve all conversations from all channels

    This gets conversations from the "All channels" endpoint, with optional filtering
    by name and tags.

    Args:
        user_id: User ID
        account_id: Account ID
        limit: Maximum number of results to return (default: 100)
        offset: Pagination offset (default: 0)
        name: Optional search filter for contact name
        tag_ids: Optional comma-separated list of tag IDs to filter by

    Returns:
        List of all conversations
    """
    params = {}
    if limit is not None:
        params["limit"] = limit
    if offset is not None:
        params["offset"] = offset
    if name is not None:
        params["name"] = name
    if tag_ids is not None:
        params["tagIds"] = tag_ids

    result = await client.request(
        "GET",
        f"/users/{user_id}/accounts/{account_id}/conversations",
        params=params,
    )
    return result


@mcp.tool()
async def get_campaign_conversations(
    user_id: str,
    account_id: str,
    campaign_id: str,
    limit: int = 100,
    offset: int = 0,
    name: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Retrieve conversations from a specific campaign

    This gets all conversations associated with a particular campaign.

    Args:
        user_id: User ID
        account_id: Account ID
        campaign_id: Campaign ID to get conversations from
        limit: Maximum number of results to return (default: 100)
        offset: Pagination offset (default: 0)
        name: Optional search filter for contact name

    Returns:
        Conversations from the specified campaign
    """
    params = {}
    if limit is not None:
        params["limit"] = limit
    if offset is not None:
        params["offset"] = offset
    if name is not None:
        params["name"] = name

    result = await client.request(
        "GET",
        f"/users/{user_id}/accounts/{account_id}/campaigns/{campaign_id}/messages",
        params=params,
    )
    return result


@mcp.tool()
async def get_messages_for_leads(
    user_id: str,
    account_id: str,
    lead_ids: Optional[List[str]] = None,
    limit: int = 100,
) -> Dict[str, Any]:
    """
    Retrieve messages for specific leads

    This gets conversation messages associated with specific lead IDs.

    Args:
        user_id: User ID
        account_id: Account ID
        lead_ids: Optional list of lead IDs to get messages for
        limit: Maximum number of results to return (default: 100)

    Returns:
        Messages for the specified leads
    """
    params = {}
    if lead_ids:
        params["leadIds"] = json.dumps(lead_ids)
    if limit is not None:
        params["limit"] = limit

    result = await client.request(
        "GET",
        f"/users/{user_id}/accounts/{account_id}/conversations/leads",
        params=params,
    )
    return result


@mcp.tool()
async def mark_messages_as_seen(
    user_id: str,
    account_id: str,
    thread: str,
) -> Dict[str, Any]:
    """
    Mark messages in a thread as seen

    This marks all messages in a specific conversation thread as read/seen.

    Args:
        user_id: User ID
        account_id: Account ID
        thread: Thread ID to mark as seen

    Returns:
        Success confirmation
    """
    result = await client.request(
        "PATCH",
        f"/users/{user_id}/accounts/{account_id}/conversations/{thread}/seen",
    )
    return result


@mcp.tool()
async def send_new_email(
    user_id: str,
    account_id: str,
    recipient: str,
    subject: str,
    content: str,
    signature_id: int,
) -> Dict[str, Any]:
    """
    Send a new email to a recipient

    This sends a new email through the platform to a recipient who may not have
    an existing thread.

    Args:
        user_id: User ID
        account_id: Account ID
        recipient: Email address of the recipient
        subject: Email subject line
        content: Email body content (can include HTML)
        signature_id: ID of the signature to use

    Returns:
        Sent email details
    """
    json_data = {
        "recipient": recipient,
        "subject": subject,
        "content": content,
        "signatureId": signature_id,
    }

    result = await client.request(
        "POST",
        f"/users/{user_id}/accounts/{account_id}/conversations/send_email_manually",
        json_data=json_data,
    )
    return result


@mcp.tool()
async def send_email_reply(
    user_id: str,
    account_id: str,
    thread: str,
    message: str,
    lead_id: int,
    campaign_id: int,
    recipient: str,
) -> Dict[str, Any]:
    """
    Send an email reply to an existing thread

    This sends a reply to an existing email conversation thread.

    Args:
        user_id: User ID
        account_id: Account ID
        thread: Thread ID to reply to
        message: Email message content
        lead_id: Lead ID associated with this conversation
        campaign_id: Campaign ID associated with this conversation
        recipient: Email address of the recipient

    Returns:
        Sent email reply details
    """
    json_data = {
        "message": message,
        "leadId": lead_id,
        "campaignId": campaign_id,
        "recipient": recipient,
    }

    result = await client.request(
        "POST",
        f"/users/{user_id}/accounts/{account_id}/conversations/{thread}/email",
        json_data=json_data,
    )
    return result


@mcp.tool()
async def send_linkedin_message(
    user_id: str,
    account_id: str,
    message: str,
    linkedin_user_id: int,
    public_identifier: str,
    campaign_id: int,
    lead_id: int,
) -> Dict[str, Any]:
    """
    Send a LinkedIn message to an existing thread

    This sends a LinkedIn message to an existing conversation in the platform's inbox.

    Args:
        user_id: User ID
        account_id: Account ID
        message: Message content to send
        linkedin_user_id: LinkedIn user ID of the recipient
        public_identifier: LinkedIn public identifier of the recipient
        campaign_id: Campaign ID associated with this conversation
        lead_id: Lead ID associated with this conversation

    Returns:
        Sent LinkedIn message details
    """
    json_data = {
        "message": message,
        "linkedinUserId": linkedin_user_id,
        "publicIdentifier": public_identifier,
        "campaignId": campaign_id,
        "leadId": lead_id,
    }

    result = await client.request(
        "POST",
        f"/users/{user_id}/accounts/{account_id}/conversations/send_message",
        json_data=json_data,
    )
    return result


@mcp.tool()
async def get_lead_messages(
    user_id: str,
    account_id: str,
    lead_id: str,
) -> Dict[str, Any]:
    """
    Retrieve all messages for a specific lead

    This gets all conversation messages associated with a particular lead.

    Args:
        user_id: User ID
        account_id: Account ID
        lead_id: Lead ID to get messages for

    Returns:
        All messages for the specified lead
    """
    result = await client.request(
        "GET",
        f"/users/{user_id}/accounts/{account_id}/conversations/leads/{lead_id}",
    )
    return result


# ============================================================================
# WEBHOOKS TOOLS (6 endpoints)
# ============================================================================


@mcp.tool()
async def create_webhook(
    user_id: str,
    account_id: str,
    webhooks: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Create a non-global webhook

    This creates a webhook that listens for specific events. Non-global webhooks
    are scoped to specific campaigns or resources.

    Args:
        user_id: User ID
        account_id: Account ID
        webhooks: List of webhook configurations, each containing:
            - url: Webhook endpoint URL
            - events: List of event types to subscribe to
            - campaignId: (Optional) Campaign ID to scope webhook to

    Returns:
        Created webhook details
    """
    json_data = {"webhooks": webhooks}

    result = await client.request(
        "POST",
        f"/users/{user_id}/accounts/{account_id}/webhooks",
        json_data=json_data,
    )
    return result


@mcp.tool()
async def create_global_webhook(
    user_id: str,
    account_id: str,
    webhooks: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Create a global webhook

    This creates a webhook that listens for events across all campaigns and resources
    in the account.

    Args:
        user_id: User ID
        account_id: Account ID
        webhooks: List of webhook configurations, each containing:
            - url: Webhook endpoint URL
            - events: List of event types to subscribe to

    Returns:
        Created global webhook details
    """
    json_data = {"webhooks": webhooks}

    result = await client.request(
        "POST",
        f"/users/{user_id}/accounts/{account_id}/global_webhook",
        json_data=json_data,
    )
    return result


@mcp.tool()
async def list_webhooks(
    user_id: str,
    account_id: str,
    limit: int = 30,
    offset: int = 0,
) -> Dict[str, Any]:
    """
    List non-global webhooks

    This retrieves all non-global webhooks configured for the account.

    Args:
        user_id: User ID
        account_id: Account ID
        limit: Maximum number of results to return (default: 30)
        offset: Pagination offset (default: 0)

    Returns:
        List of non-global webhooks
    """
    params = {}
    if limit is not None:
        params["limit"] = limit
    if offset is not None:
        params["offset"] = offset

    result = await client.request(
        "GET",
        f"/users/{user_id}/accounts/{account_id}/webhooks",
        params=params,
    )
    return result


@mcp.tool()
async def list_global_webhooks(
    user_id: str,
    account_id: str,
    limit: int = 30,
    offset: int = 0,
) -> Dict[str, Any]:
    """
    List global webhooks

    This retrieves all global webhooks configured for the account.

    Args:
        user_id: User ID
        account_id: Account ID
        limit: Maximum number of results to return (default: 30)
        offset: Pagination offset (default: 0)

    Returns:
        List of global webhooks
    """
    params = {}
    if limit is not None:
        params["limit"] = limit
    if offset is not None:
        params["offset"] = offset

    result = await client.request(
        "GET",
        f"/users/{user_id}/accounts/{account_id}/global_webhooks",
        params=params,
    )
    return result


@mcp.tool()
async def delete_webhook(
    user_id: str,
    account_id: str,
    webhook_id: str,
) -> Dict[str, Any]:
    """
    Delete a non-global webhook

    This removes a specific non-global webhook by its ID.

    Args:
        user_id: User ID
        account_id: Account ID
        webhook_id: Webhook ID to delete

    Returns:
        Success confirmation
    """
    result = await client.request(
        "DELETE",
        f"/users/{user_id}/accounts/{account_id}/webhooks/{webhook_id}",
    )
    return result


@mcp.tool()
async def delete_global_webhook(
    user_id: str,
    account_id: str,
    array_of_actions: List[str],
    array_of_ids: List[int],
    url: str,
) -> Dict[str, Any]:
    """
    Delete a global webhook

    This removes a specific global webhook by matching URL and event subscriptions.

    Args:
        user_id: User ID
        account_id: Account ID
        array_of_actions: List of event action types the webhook was subscribed to
        array_of_ids: List of resource IDs associated with the webhook
        url: Webhook URL to delete

    Returns:
        Success confirmation
    """
    json_data = {
        "arrayOfActions": array_of_actions,
        "arrayOfIds": array_of_ids,
        "url": url,
    }

    result = await client.request(
        "POST",
        f"/users/{user_id}/accounts/{account_id}/delete_global_webhook",
        json_data=json_data,
    )
    return result


@mcp.tool()
async def get_description_for_id_type(
    ids: str,
) -> str:
    """
    Get descriptions for identity type IDs (resolves internal IDs to human-readable labels).

    Args:
        ids: Comma-separated identity type IDs to look up

    Returns:
        JSON string with identity type descriptions for the given IDs
    """
    result = await client.request("GET", f"/identityType/ids/{ids}")
    return json.dumps(result, indent=2)


# ============================================================================
# RESOURCES
# ============================================================================


@mcp.resource("multilead://config", name="Multilead MCP Server Configuration", description="Current server configuration including API base URL, timeout settings, and debug mode status")
def get_server_config() -> str:
    """
    Get current Multilead MCP server configuration

    Returns server configuration including API base URL, timeout settings,
    and debug mode status (API key is never exposed).
    """
    config_info = {
        "server_name": "Multilead Open API",
        "version": "1.0.0",
        "base_url": config.base_url,
        "timeout_seconds": config.timeout,
        "debug_mode": config.debug,
        "api_key_configured": bool(config.api_key),
        "api_key_prefix": config.api_key[:8] + "..." if config.api_key else "NOT_SET",
    }

    return f"""# Multilead MCP Server Configuration

**Server Name:** {config_info['server_name']}
**Version:** {config_info['version']}
**API Base URL:** {config_info['base_url']}
**Timeout:** {config_info['timeout_seconds']} seconds
**Debug Mode:** {config_info['debug_mode']}
**API Key Status:** {'Configured' if config_info['api_key_configured'] else 'NOT CONFIGURED'}
**API Key Prefix:** {config_info['api_key_prefix']}

## Environment Variables
- MULTILEAD_API_KEY: {'Set' if config_info['api_key_configured'] else 'NOT SET'}
- MULTILEAD_BASE_URL: {config_info['base_url']}
- MULTILEAD_TIMEOUT: {config_info['timeout_seconds']}
- MULTILEAD_DEBUG: {config_info['debug_mode']}

## Available Tool Categories (76 tools)

1. **Lead Management** (14 tools) - Add leads, pause/resume, tags, campaigns
2. **Campaign Management** (6 tools) - Create, export, campaign info
3. **Users & Seats** (15 tools) - User management, seat provisioning
4. **Conversations** (12 tools) - Email and LinkedIn threads
5. **Webhooks** (6 tools) - Event subscriptions
6. **Seats** (3 tools) - Tags, LinkedIn connect/disconnect
7. **Statistics** (4 tools) - Campaign stats, CSV export
8. **Blacklist** (4 tools) - Keyword blacklists
9. **Warmup** (1 tool) - InboxFlare warmup
10. **Team Management** (6 tools) - Teams, roles, members
11. **Settings** (1 tool) - Identity type resolution

## Getting Started

To use this server, ensure you have:
1. A valid Multilead API key set as MULTILEAD_API_KEY in your .env
2. Network access to {config_info['base_url']}

For full API documentation, visit: https://docs.multilead.co/api-reference
"""


@mcp.resource("multilead://stats", name="Multilead API Statistics", description="API usage statistics and account information including lead count, campaign count, and rate limits")
async def get_api_stats() -> str:
    """
    Get Multilead API usage statistics and account information

    Returns current account statistics including lead count, campaign count,
    and API rate limit information.
    """
    try:
        # Fetch account stats from API
        stats = await client.request("GET", "/v1/account/stats")

        # Extract nested data if present
        account = stats.get('account', {})
        usage = stats.get('usage', {})

        return f"""# Multilead API Statistics

**Total Leads:** {account.get('leads_count', stats.get('total_leads', 'N/A'))}
**Total Campaigns:** {account.get('campaigns_count', stats.get('campaigns_count', 'N/A'))}
**Active Campaigns:** {account.get('active_campaigns', stats.get('active_campaigns', 'N/A'))}
**Total Conversations:** {account.get('conversations_count', stats.get('total_conversations', 'N/A'))}
**API Requests (Today):** {usage.get('api_calls_today', stats.get('api_requests_today', 'N/A'))}
**Rate Limit:** {usage.get('rate_limit', stats.get('rate_limit', 'N/A'))} requests/hour
**Rate Limit Remaining:** {usage.get('rate_limit_remaining', stats.get('rate_limit_remaining', 'N/A'))}

Last updated: {datetime.now().isoformat()}
"""
    except Exception as e:
        return f"# Multilead API Statistics\n\nError fetching statistics: {str(e)}"


# ============================================================================
# PROMPTS - Example implementations
# ============================================================================


@mcp.prompt()
def lead_enrichment_prompt() -> str:
    """
    Prompt template for enriching lead data with AI

    Provides guidance for analyzing and enriching lead information including
    company research, contact validation, and lead scoring.
    """
    return """You are a lead enrichment specialist. Your task is to analyze and enrich lead data.

Given a lead with basic information (email, name, company), please:

1. **Validate Contact Information:**
   - Verify email format and domain validity
   - Check if company name is legitimate
   - Identify potential data quality issues

2. **Company Research:**
   - Provide industry classification
   - Estimate company size and revenue range
   - Identify key products or services
   - Note any recent news or funding events

3. **Lead Scoring:**
   - Assign a lead score (1-100) based on:
     * Company size and industry fit
     * Contact title and seniority
     * Email domain quality (corporate vs generic)
     * Data completeness

4. **Enrichment Suggestions:**
   - List missing data points that should be collected
   - Suggest relevant tags or categories
   - Recommend next best actions for outreach

5. **Red Flags:**
   - Identify any suspicious patterns
   - Note potential spam or invalid contacts
   - Highlight data inconsistencies

Please provide your analysis in a structured format that can be used to update the lead record.
"""


@mcp.prompt()
def campaign_analysis_prompt() -> str:
    """
    Prompt template for analyzing campaign performance

    Provides guidance for evaluating email campaign metrics and generating
    actionable insights for optimization.
    """
    return """You are a campaign performance analyst. Your task is to analyze email campaign data.

Given campaign metrics (open rate, click rate, conversions, etc.), please:

1. **Performance Assessment:**
   - Compare metrics against industry benchmarks
   - Identify high-performing and underperforming elements
   - Calculate ROI and cost per acquisition

2. **Trend Analysis:**
   - Analyze performance over time
   - Identify seasonal patterns or anomalies
   - Compare to previous campaigns

3. **Audience Insights:**
   - Segment performance by audience characteristics
   - Identify most engaged segments
   - Note segments requiring re-engagement

4. **Optimization Recommendations:**
   - Suggest subject line improvements
   - Recommend send time optimizations
   - Propose A/B testing opportunities
   - Advise on content and CTA enhancements

5. **Next Steps:**
   - Prioritize action items by impact
   - Set specific, measurable improvement goals
   - Recommend follow-up campaigns or sequences

Please provide actionable insights that can immediately improve campaign performance.
"""


# ============================================================================
# Server Execution
# ============================================================================

if __name__ == "__main__":
    """
    Server Entry Point

    Supports both STDIO and HTTP transports based on environment variables:
    - TRANSPORT: "stdio" (default) or "http"
    - HOST: Default "0.0.0.0" for HTTP
    - PORT: Default 8000 for HTTP
    - LOG_LEVEL: Default "INFO"

    Examples:
        # STDIO mode (default - for Claude Desktop/Code)
        python server.py

        # HTTP mode (for web services)
        TRANSPORT=http python server.py

        # HTTP with custom port
        TRANSPORT=http PORT=3000 python server.py
    """
    import sys

    # Read transport configuration from environment
    transport = os.getenv("TRANSPORT", "stdio").lower()
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    # Validate transport
    if transport not in ["stdio", "http"]:
        print(f"Error: Invalid TRANSPORT value '{transport}'. Must be 'stdio' or 'http'.", file=sys.stderr)
        sys.exit(1)

    if transport == "http":
        print(f"Starting Multilead MCP Server in HTTP mode on {host}:{port}", file=sys.stderr)
        print(f"MCP endpoint: http://{host}:{port}/mcp", file=sys.stderr)
        print(f"Log level: {log_level}", file=sys.stderr)
        mcp.run(transport="http", host=host, port=port)
    else:
        print("Starting Multilead MCP Server in STDIO mode", file=sys.stderr)
        print(f"Log level: {log_level}", file=sys.stderr)
        mcp.run()
