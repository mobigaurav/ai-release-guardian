# AI Release Guardian - Phase 1 MVP

**Automated Integration & Automation Test Generation for GitHub PRs**

## What It Does

Reads GitHub PRs + Jira AC → Auto-generates integration test scenarios + automation test cases → Posts PR comment with test suggestions & risk flags.

## Phase 1 Scope

✅ PR diff analysis + Jira AC mapping
✅ Integration test scenario generation
✅ Automation test case generation (API flows, E2E paths)
✅ Risk scoring for API/DB changes
✅ MCP server endpoints
✅ GitHub webhook integration
✅ Lambda deployment ready

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/

# Start MCP server (local dev)
python src/mcp/server.py

# Deploy to AWS Lambda
cd lambda && sam deploy
```

## Architecture

```
GitHub Webhook (PR opened/updated)
    ↓
Lambda Handler
    ↓
MCP Server
    ├─ Planner Agent (analyze PR diff + Jira)
    ├─ Test Generator Agent (create test scenarios)
    ├─ Risk Scorer Agent (flag risky changes)
    └─ Rollback Planner Agent
    ↓
GitHub PR Comment (test suggestions + risk)
```

## Project Structure

```
ai-release-guardian/
├── src/
│   ├── agents/               # AI agents for analysis
│   │   ├── planner.py       # PR + Jira analysis
│   │   ├── test_generator.py # Integration & automation tests
│   │   ├── risk_scorer.py   # Risk assessment
│   │   └── rollback.py      # Rollback planning
│   ├── integrations/
│   │   ├── github.py        # GitHub API wrapper
│   │   ├── jira.py          # Jira API wrapper
│   │   └── claude.py        # Anthropic Claude integration
│   ├── mcp/
│   │   └── server.py        # MCP server implementation
│   ├── models/
│   │   └── schemas.py       # Data models
│   └── utils/
│       └── logger.py        # Logging setup
├── lambda/
│   ├── handler.py           # GitHub webhook handler
│   ├── requirements.txt
│   └── template.yaml        # SAM template
├── tests/
│   ├── test_agents.py
│   └── test_integrations.py
├── requirements.txt         # Python dependencies
└── .env.example             # Environment variables
```

## Configuration

Create `.env`:
```
GITHUB_TOKEN=ghp_xxxx
JIRA_URL=https://your-jira.atlassian.net
JIRA_USER=your-email@company.com
JIRA_API_TOKEN=xxxx
CLAUDE_API_KEY=sk-xxxx
```

## Development

1. **Add a new agent**: Create `src/agents/my_agent.py`
2. **Add MCP endpoint**: Register in `src/mcp/server.py`
3. **Test locally**: `python src/mcp/server.py`
4. **Deploy**: `sam deploy`

## Next Steps (Phase 2+)

- [ ] Release confidence scoring dashboard
- [ ] QA team metrics & velocity tracking
- [ ] Deployment gate automation
- [ ] Slack notifications
- [ ] Multi-repo support
