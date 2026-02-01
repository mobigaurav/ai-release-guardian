# Getting Started - AI Release Guardian Phase 1

## Prerequisites

- Python 3.11+
- pip or poetry
- AWS account (for Lambda deployment)
- GitHub token with `repo` scope
- Jira API token (optional, for AC extraction)
- Claude API key from Anthropic

## Installation

### 1. Clone & Setup

```bash
cd ai-release-guardian
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env` with:
- `GITHUB_TOKEN`: Create at https://github.com/settings/tokens (scopes: `repo`, `read:org`)
- `JIRA_URL`: Your Jira instance URL
- `JIRA_USER`: Your Jira email
- `JIRA_API_TOKEN`: Create at https://id.atlassian.com/manage-profile/security/api-tokens
- `CLAUDE_API_KEY`: Get from https://console.anthropic.com/

## Running Locally

### Start MCP Server

```bash
python src/mcp/server.py
```

Server will run on `http://localhost:8000`

#### Test the API

```bash
# Health check
curl http://localhost:8000/health

# Generate tests
curl -X POST http://localhost:8000/generate-tests \
  -H "Content-Type: application/json" \
  -d '{
    "code_diff": "def calculate_total():\n    return sum(...)",
    "acceptance_criteria": ["Should calculate total correctly"],
    "file_types": {"backend": ["services/calculator.py"]}
  }'

# Get risk score
curl -X POST http://localhost:8000/release-risk-score \
  -H "Content-Type: application/json" \
  -d '{
    "changes_summary": "Added user authentication module",
    "file_types": {"backend": ["auth/login.py"]},
    "total_changes": 45
  }'
```

### Run Tests

```bash
pytest tests/ -v
```

## Deployment to AWS Lambda

### 1. Build SAM Package

```bash
cd lambda
sam build
```

### 2. Deploy

```bash
sam deploy \
  --parameter-overrides \
    GitHubToken=your_token \
    JiraUrl=https://your-jira.atlassian.net \
    JiraUser=your-email@company.com \
    JiraApiToken=your_token \
    ClaudeApiKey=your_key
```

The deployment will output the GitHub webhook URL.

### 3. Configure GitHub Webhook

1. Go to your GitHub repo → Settings → Webhooks
2. Add new webhook:
   - **Payload URL**: Use the URL from SAM deployment output
   - **Content type**: `application/json`
   - **Events**: Pull Requests (select only `opened` and `synchronize`)
   - **Active**: ✅

## How It Works - Phase 1

### 1. PR Opened/Updated
GitHub sends webhook to Lambda → Lambda triggers MCP analysis

### 2. Analysis Pipeline
```
PR Diff + Jira AC
    ↓
Planner Agent (extract context)
    ↓
Test Generator Agent (create test scenarios)
    ↓
Risk Scorer Agent (assess risk)
    ↓
PR Comment Posted
```

### 3. PR Comment Output
```markdown
## 🤖 AI Release Guardian Analysis

### 🧪 Auto-Generated Test Scenarios (5 total)
- Integration Tests: 2 ✓
- Automation Tests: 2 ✓
- E2E Flows: 1 ✓

### 🟡 Release Risk Assessment
- Risk Score: 35/100 (MEDIUM)
- Deployment Confidence: 65%
- Manual Review Required: No ✓

### 📋 Linked Jira Tickets
PROJ-123, PROJ-124

### 💡 Recommendations
- Run full integration test suite
- Perform smoke tests in staging
- Monitor error rates post-deployment
```

## Project Structure

```
src/
├── agents/              # AI agents
│   ├── planner.py      # PR + Jira analysis
│   ├── test_generator.py  # Test scenario creation
│   ├── risk_scorer.py  # Risk assessment
│   └── rollback.py     # Rollback planning
├── integrations/        # External APIs
│   ├── github.py       # GitHub API
│   ├── jira.py         # Jira API
│   └── claude.py       # Claude AI
├── mcp/
│   └── server.py       # MCP server implementation
└── models/
    └── schemas.py      # Data models

lambda/
├── handler.py          # Lambda entry point
└── template.yaml       # SAM template

tests/
├── test_agents.py
└── test_integrations.py
```

## MCP Server Endpoints

### POST `/analyze-release`
Full PR analysis with tests + risk

**Request:**
```json
{
  "repo_owner": "myorg",
  "repo_name": "myrepo",
  "pr_number": 123
}
```

**Response:**
```json
{
  "success": true,
  "pr_number": 123,
  "analysis": {
    "tests_generated": 5,
    "risk_score": 35,
    "confidence": 65,
    "risk_flags": ["API changes"],
    "requires_manual_review": false
  }
}
```

### POST `/generate-tests`
Generate test scenarios from code

**Request:**
```json
{
  "code_diff": "function new_feature() {...}",
  "acceptance_criteria": ["Should work correctly"],
  "file_types": {"backend": ["app.js"]}
}
```

### POST `/release-risk-score`
Score the risk of a deployment

**Request:**
```json
{
  "changes_summary": "Added payment processing",
  "file_types": {"backend": ["payment.py"]},
  "total_changes": 150
}
```

### POST `/rollback-plan`
Generate rollback procedures

**Request:**
```json
{
  "release_id": "v1.2.3",
  "changed_files": ["app.py", "database.sql"],
  "file_types": {"backend": ["app.py"], "database": ["database.sql"]},
  "risk_flags": ["Database migration"]
}
```

## Next Steps

### Phase 2 Ideas
- [ ] PR comment includes test code skeleton
- [ ] Automatic test execution in CI/CD
- [ ] Release confidence gate for auto-merge
- [ ] Slack notifications with risk alerts
- [ ] QA team dashboard with metrics
- [ ] Multi-repo support

### Metrics to Track
- Time saved on manual test case writing
- PR cycle time improvement
- Bugs caught by Guardian vs missed
- QA team velocity gain

## Troubleshooting

### Claude API Returns Rate Limited
- Check API key validity
- Implement request queuing/backoff (in Phase 2)

### GitHub Webhook Not Triggering
- Verify webhook URL in GitHub settings
- Check Lambda CloudWatch logs
- Ensure webhook events filter set to "opened" and "synchronize"

### Jira Tickets Not Found
- Verify Jira credentials
- Ensure ticket ID format is correct (e.g., PROJ-123)
- Check Jira API token has read access

## Support & Questions

See README.md for project overview.

---

**Phase 1 Complete!** 🎉 This MVP demonstrates the core concept. Ready to measure QA team impact?
