# Cats → Skylead Integration

With both MCP servers configured, you can now bridge your ATS with LinkedIn outreach!

## Configuration

The MCP servers are configured in `~/.config/claude/claude_mcp_config.json`:

- **Cats MCP**: Remote server at https://catsmcp.fastmcp.app/mcp
- **Multilead MCP**: Local server with your API credentials

## Integration Flow

### 1. Get Candidates from Cats ATS

```
Use Cats MCP tools:
- search_candidates(filters={"job_title": "Heavy Equipment Mechanic"})
- list_candidates(pipeline_id=..., stage_id=...)
- get_candidate(candidate_id=...)
```

### 2. Push to Skylead Campaign

```
Use Multilead MCP tools:
- add_leads_to_campaign(
    campaign_id="374384",
    email=candidate.email,
    custom_fields={
      "firstName": candidate.first_name,
      "lastName": candidate.last_name,
      "phone": candidate.phone,
      "occupation": candidate.job_title,
      "ats_id": candidate.id,
      "ats_source": "Cats"
    }
  )
```

### 3. Track in Both Systems

```
- Skylead runs LinkedIn outreach automatically
- Responses sync back to Skylead inbox
- Update candidate in Cats with LinkedIn engagement data
```

## Example Workflow

**Scenario**: New candidates added to "Heavy Equipment Mechanics" pipeline in Cats

1. Query Cats for new candidates in specific stage
2. For each candidate:
   - Extract email, name, phone from Cats
   - Add to Skylead campaign "Underground Heavy Equipment Mechanics" (ID: 374384)
   - Tag candidate in Cats as "LinkedIn Outreach Active"
3. Monitor responses in Skylead
4. Update candidate status in Cats based on engagement

## Automation Options

### Option 1: Manual Trigger
Ask Claude Code to sync candidates when needed

### Option 2: Scheduled Sync
Create a cron job that calls both MCP servers

### Option 3: Webhook Integration
- Cats webhook → Your middleware → Multilead MCP → Skylead
- Skylead webhook → Your middleware → Cats MCP → Update candidate

## Your Active Campaign

**Campaign ID**: 374384
**Name**: Underground Heavy Equipment Mechanics
**Current Leads**: 681
**Status**: Active

Ready to receive candidates from your Cats ATS!
