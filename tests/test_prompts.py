"""
Test suite for Multilead MCP server prompts.

Tests the 2 prompts:
- lead_enrichment_prompt - AI guidance for enriching lead data
- campaign_analysis_prompt - AI guidance for campaign performance analysis
"""

import pytest
from fastmcp.client import Client
from fastmcp.client.transports import FastMCPTransport


@pytest.mark.asyncio
async def test_list_prompts(mcp_client: Client[FastMCPTransport]):
    """Test listing all available prompts."""
    prompts = await mcp_client.list_prompts()

    assert len(prompts) == 2

    # Check for lead enrichment prompt
    lead_prompt = next((p for p in prompts if p.name == "lead_enrichment_prompt"), None)
    assert lead_prompt is not None
    assert "enrich" in lead_prompt.description.lower()

    # Check for campaign analysis prompt
    campaign_prompt = next((p for p in prompts if p.name == "campaign_analysis_prompt"), None)
    assert campaign_prompt is not None
    assert "campaign" in campaign_prompt.description.lower()


@pytest.mark.asyncio
async def test_get_lead_enrichment_prompt(mcp_client: Client[FastMCPTransport]):
    """Test retrieving the lead enrichment prompt."""
    result = await mcp_client.get_prompt("lead_enrichment_prompt", arguments={})

    assert result is not None
    assert len(result.messages) > 0

    # The prompt should contain guidance for lead enrichment
    prompt_text = result.messages[0].content.text
    assert "lead" in prompt_text.lower()
    assert "enrich" in prompt_text.lower() or "data" in prompt_text.lower()


@pytest.mark.asyncio
async def test_lead_enrichment_prompt_content_structure(mcp_client: Client[FastMCPTransport]):
    """Test that lead enrichment prompt has proper structure."""
    result = await mcp_client.get_prompt("lead_enrichment_prompt", arguments={})

    prompt_text = result.messages[0].content.text

    # Should contain guidance sections
    assert len(prompt_text) > 100  # Substantial content

    # Should mention key aspects of lead enrichment
    text_lower = prompt_text.lower()
    keywords = ["lead", "information", "data", "contact", "profile"]
    assert any(keyword in text_lower for keyword in keywords)


@pytest.mark.asyncio
async def test_get_campaign_analysis_prompt(mcp_client: Client[FastMCPTransport]):
    """Test retrieving the campaign analysis prompt."""
    result = await mcp_client.get_prompt("campaign_analysis_prompt", arguments={})

    assert result is not None
    assert len(result.messages) > 0

    # The prompt should contain guidance for campaign analysis
    prompt_text = result.messages[0].content.text
    assert "campaign" in prompt_text.lower()
    assert any(
        keyword in prompt_text.lower()
        for keyword in ["performance", "analysis", "metrics", "analytics"]
    )


@pytest.mark.asyncio
async def test_campaign_analysis_prompt_content_structure(mcp_client: Client[FastMCPTransport]):
    """Test that campaign analysis prompt has proper structure."""
    result = await mcp_client.get_prompt("campaign_analysis_prompt", arguments={})

    prompt_text = result.messages[0].content.text

    # Should contain guidance sections
    assert len(prompt_text) > 100  # Substantial content

    # Should mention key metrics or analysis concepts
    text_lower = prompt_text.lower()
    metrics_keywords = ["open", "click", "reply", "metric", "rate", "performance", "analysis"]
    assert any(keyword in text_lower for keyword in metrics_keywords)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "prompt_name",
    [
        "lead_enrichment_prompt",
        "campaign_analysis_prompt",
    ],
)
async def test_prompt_without_arguments(
    mcp_client: Client[FastMCPTransport], prompt_name: str
):
    """Test that prompts work without arguments."""
    result = await mcp_client.get_prompt(prompt_name, arguments={})

    assert result is not None
    assert len(result.messages) > 0
    assert len(result.messages[0].content.text) > 0


@pytest.mark.asyncio
async def test_invalid_prompt_name(mcp_client: Client[FastMCPTransport]):
    """Test accessing a non-existent prompt."""
    with pytest.raises(Exception):  # Should raise error for invalid prompt
        await mcp_client.get_prompt("nonexistent_prompt", arguments={})


@pytest.mark.asyncio
async def test_prompt_metadata(mcp_client: Client[FastMCPTransport]):
    """Test that prompts have proper metadata."""
    prompts = await mcp_client.list_prompts()

    for prompt in prompts:
        # Each prompt should have required fields
        assert prompt.name is not None
        assert len(prompt.name) > 0
        assert prompt.description is not None
        assert len(prompt.description) > 0

        # Names should be valid
        assert prompt.name in ["lead_enrichment_prompt", "campaign_analysis_prompt"]


@pytest.mark.asyncio
async def test_prompt_message_format(mcp_client: Client[FastMCPTransport]):
    """Test that prompts return properly formatted messages."""
    result = await mcp_client.get_prompt("lead_enrichment_prompt", arguments={})

    assert result is not None
    assert hasattr(result, "messages")
    assert len(result.messages) > 0

    # First message should have content
    message = result.messages[0]
    assert hasattr(message, "content")
    assert hasattr(message.content, "text")
    assert isinstance(message.content.text, str)


@pytest.mark.asyncio
async def test_lead_enrichment_prompt_provides_guidance(mcp_client: Client[FastMCPTransport]):
    """Test that lead enrichment prompt provides actionable guidance."""
    result = await mcp_client.get_prompt("lead_enrichment_prompt", arguments={})

    prompt_text = result.messages[0].content.text

    # Should provide instructions or guidance
    # Prompts typically include action words
    action_words = ["analyze", "identify", "extract", "find", "determine", "use", "check"]
    text_lower = prompt_text.lower()
    assert any(word in text_lower for word in action_words)


@pytest.mark.asyncio
async def test_campaign_analysis_prompt_provides_guidance(mcp_client: Client[FastMCPTransport]):
    """Test that campaign analysis prompt provides actionable guidance."""
    result = await mcp_client.get_prompt("campaign_analysis_prompt", arguments={})

    prompt_text = result.messages[0].content.text

    # Should provide instructions for analysis
    action_words = ["analyze", "evaluate", "assess", "review", "calculate", "measure"]
    text_lower = prompt_text.lower()
    assert any(word in text_lower for word in action_words)


@pytest.mark.asyncio
async def test_prompts_are_distinct(mcp_client: Client[FastMCPTransport]):
    """Test that the two prompts have different content."""
    lead_result = await mcp_client.get_prompt("lead_enrichment_prompt", arguments={})
    campaign_result = await mcp_client.get_prompt("campaign_analysis_prompt", arguments={})

    lead_text = lead_result.messages[0].content.text
    campaign_text = campaign_result.messages[0].content.text

    # The prompts should have different content
    assert lead_text != campaign_text

    # They should focus on different topics
    assert "lead" in lead_text.lower() or "contact" in lead_text.lower()
    assert "campaign" in campaign_text.lower()


@pytest.mark.asyncio
async def test_lead_enrichment_prompt_mentions_relevant_fields(
    mcp_client: Client[FastMCPTransport]
):
    """Test that lead enrichment prompt mentions relevant lead fields."""
    result = await mcp_client.get_prompt("lead_enrichment_prompt", arguments={})

    prompt_text = result.messages[0].content.text.lower()

    # Should mention common lead fields or concepts
    lead_concepts = [
        "email",
        "name",
        "company",
        "position",
        "contact",
        "profile",
        "linkedin",
        "social",
    ]

    # At least some of these should be mentioned
    matches = sum(1 for concept in lead_concepts if concept in prompt_text)
    assert matches >= 2, "Prompt should mention at least 2 relevant lead concepts"


@pytest.mark.asyncio
async def test_campaign_analysis_prompt_mentions_relevant_metrics(
    mcp_client: Client[FastMCPTransport]
):
    """Test that campaign analysis prompt mentions relevant metrics."""
    result = await mcp_client.get_prompt("campaign_analysis_prompt", arguments={})

    prompt_text = result.messages[0].content.text.lower()

    # Should mention email campaign metrics or concepts
    campaign_concepts = [
        "open",
        "click",
        "reply",
        "bounce",
        "sent",
        "delivered",
        "engagement",
        "conversion",
        "rate",
        "metric",
    ]

    # At least some of these should be mentioned
    matches = sum(1 for concept in campaign_concepts if concept in prompt_text)
    assert matches >= 2, "Prompt should mention at least 2 relevant campaign concepts"


@pytest.mark.asyncio
async def test_prompt_consistency_across_calls(mcp_client: Client[FastMCPTransport]):
    """Test that prompts return consistent content across multiple calls."""
    # First call
    result_1 = await mcp_client.get_prompt("lead_enrichment_prompt", arguments={})
    text_1 = result_1.messages[0].content.text

    # Second call
    result_2 = await mcp_client.get_prompt("lead_enrichment_prompt", arguments={})
    text_2 = result_2.messages[0].content.text

    # Should return the same content (prompts are static templates)
    assert text_1 == text_2


@pytest.mark.asyncio
async def test_prompts_have_reasonable_length(mcp_client: Client[FastMCPTransport]):
    """Test that prompts have reasonable length (not too short or too long)."""
    prompts = await mcp_client.list_prompts()

    for prompt_info in prompts:
        result = await mcp_client.get_prompt(prompt_info.name, arguments={})
        text = result.messages[0].content.text

        # Should be substantial but not excessively long
        assert len(text) >= 50, f"{prompt_info.name} is too short"
        assert len(text) <= 5000, f"{prompt_info.name} is too long"


@pytest.mark.asyncio
async def test_prompt_text_is_well_formed(mcp_client: Client[FastMCPTransport]):
    """Test that prompt text is well-formed and readable."""
    prompts = await mcp_client.list_prompts()

    for prompt_info in prompts:
        result = await mcp_client.get_prompt(prompt_info.name, arguments={})
        text = result.messages[0].content.text

        # Should not be empty
        assert len(text.strip()) > 0

        # Should contain alphanumeric characters
        assert any(c.isalnum() for c in text)

        # Should have reasonable structure (multiple sentences or lines)
        assert text.count(".") >= 1 or text.count("\n") >= 1
