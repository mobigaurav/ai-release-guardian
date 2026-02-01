# AI Release Guardian - Quick Reference

## What is This?

AI Release Guardian is an **automated PR analysis + test generation system** that:
- Reads GitHub PRs + Jira AC
- Auto-generates integration & automation test scenarios
- Scores release risk (0-100%)
- Posts PR comments with recommendations
- Generates rollback plans

**Problem it solves:** QA bottleneck when dev velocity (with AI assist) exceeds QA capacity.

## Quick Start (5 mins)

```bash
# 1. Navigate to project
cd /Users/gauravkumar/Desktop/pproject/myaiprojects/ai-release-guardian

# 2. Setup environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# 3. Fill in .env with your API keys (see GETTING_STARTED.md)
nano .env

# 4. Start local MCP server
python src/mcp/server.py

# 5. Test it
curl http://localhost:8000/health
```

## Key Files

| File | Purpose |
|------|---------|
| `src/agents/planner.py` | Analyzes PR + Jira context |
| `src/agents/test_generator.py` | Creates test scenarios |
| `src/agents/risk_scorer.py` | Calculates risk score |
| `src/agents/rollback.py` | Generates rollback procedures |
| `src/mcp/server.py` | API endpoints for analysis |
| `lambda/handler.py` | GitHub webhook handler |
| `lambda/template.yaml` | AWS Lambda deployment config |

## Core Concepts

### Agents (AI Workers)
1. **Planner Agent** → Reads PR diff + Jira AC, extracts context
2. **Test Generator** → Creates integration + automation + E2E test scenarios
3. **Risk Scorer** → Analyzes changes, assigns risk score (0-100)
4. **Rollback Planner** → Creates step-by-step rollback procedures

### MCP Server (Callable API)
```
POST /analyze-release        → Full PR analysis
POST /generate-tests         → Test scenarios
POST /release-risk-score    → Risk assessment
POST /rollback-plan         → Rollback steps
```

### Flow

```
GitHub PR Webhook
    ↓ (if opened/synchronize)
Lambda Handler
    ↓
MCP Server (Analysis)
    ├─ Planner (context extraction)
    ├─ Test Generator (scenarios)
    ├─ Risk Scorer (confidence %)
    ├─ Rollback Planner
    ↓
GitHub PR Comment Posted
    (Test suggestions + risk score)
```

## API Examples

### Test Generation
```bash
curl -X POST http://localhost:8000/generate-tests \
  -H "Content-Type: application/json" \
  -d '{
    "code_diff": "def new_feature():\n    pass",
    "acceptance_criteria": ["Should work"],
    "file_types": {"backend": ["app.py"]}
  }'
```

### Risk Scoring
```bash
curl -X POST http://localhost:8000/release-risk-score \
  -H "Content-Type: application/json" \
  -d '{
    "changes_summary": "Added user auth",
    "file_types": {"backend": ["auth.py"]},
    "total_changes": 45
  }'
```

## Environment Setup

Create `.env` with:
```
GITHUB_TOKEN=ghp_xxxx               # GitHub PAT
JIRA_URL=https://jira.company.com   # Jira instance
JIRA_USER=you@company.com           # Jira email
JIRA_API_TOKEN=xxxx                 # Jira API token
CLAUDE_API_KEY=sk-ant-xxxx          # Claude API key
ENV=development                     # development or production
```

## Deployment to AWS Lambda

```bash
cd lambda
sam build
sam deploy \
  --parameter-overrides \
    GitHubToken=your_token \
    JiraUrl=https://your-jira.com \
    JiraUser=your@email.com \
    JiraApiToken=token \
    ClaudeApiKey=key

# Then configure GitHub webhook with the output URL
```

## Test Data Models

```python
TestScenario(
    test_id="integration_1",
    name="test_user_creation",
    description="Test user registration",
    type="integration_test",  # or "automation_test" or "e2e_test"
    scenario_steps=["POST /users", "Verify DB"],
    expected_outcomes=["User created", "Email sent"],
    priority="high"  # or "medium", "low"
)

RiskAssessment(
    risk_score=35,              # 0-100
    confidence_percentage=65,   # 0-100 
    risk_flags=["API changes"],
    suggestions=["Run tests"],
    requires_manual_review=False
)
```

## Output Example

PR Comment posted by Guardian:
```markdown
## 🤖 AI Release Guardian Analysis

### 🧪 Auto-Generated Test Scenarios (5 total)
- Integration Tests: 2 ✓
- Automation Tests: 2 ✓  
- E2E Flows: 1 ✓

### 🟡 Release Risk Assessment
Risk Score: 35/100 (MEDIUM)
Deployment Confidence: 65%
Manual Review Required: No ✓

Risk Flags:
- ⚠️ API changes detected - verify contract compatibility
- ⚠️ Database schema changes detected - requires migration testing

### 💡 Recommendations
- Run full integration test suite
- Perform smoke tests in staging
- Monitor error rates post-deployment
```

## Running Tests

```bash
pytest tests/ -v              # Run all tests
pytest tests/test_agents.py   # Specific test file
pytest -k "test_risk"         # Run tests matching pattern
pytest --cov                  # Coverage report
```

## Phase 1 Outcomes

✅ **What Works Now:**
- PR analysis automation
- Integration test generation
- Risk scoring
- Rollback planning
- MCP server endpoints
- Lambda + webhook integration

🎯 **Metrics to Track:**
- Time saved per PR (manual test case writing)
- PR cycle time reduction
- QA team velocity improvement
- Bugs caught by Guardian

## Phase 2 Ideas

- Automated test code generation (with fixtures)
- CI/CD pipeline integration
- Release confidence gate for auto-merge
- Slack notifications
- QA dashboard with metrics
- Multi-repo support
- Custom rule configuration

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Claude API returns 429 | Implement retry backoff |
| GitHub webhook not firing | Check webhook URL in GitHub settings |
| Jira tickets not found | Verify JIRA_API_TOKEN has read access |
| Test generation is empty | Ensure Claude API key is valid |

## Key Stats

| Metric | Value |
|--------|-------|
| Lines of Code | ~1500 |
| Test Scenarios per PR | 3-8 |
| Risk Scoring Accuracy | Depends on Claude |
| Lambda Timeout | 60 seconds |
| Memory Required | 512 MB |

## Agents Breakdown

### Planner Agent
```python
analyze_pr_context() → {
    pr_info,
    jira_tickets,
    acceptance_criteria,
    file_types,
    total_changes
}
```

### Test Generator
```python
generate_tests() → {
    integration_tests: [TestScenario],
    automation_tests: [TestScenario],
    e2e_flows: [TestScenario]
}
```

### Risk Scorer
```python
score_release() → RiskAssessment {
    risk_score: 0-100,
    confidence_percentage: 0-100,
    risk_flags: [str],
    suggestions: [str],
    requires_manual_review: bool
}
```

### Rollback Planner
```python
generate_rollback_plan() → RollbackPlan {
    steps: [str],
    estimated_duration_minutes: int,
    critical_alerts: [str],
    data_backup_required: bool
}
```

---

**Next:** See `GETTING_STARTED.md` for detailed setup. See `README.md` for architecture overview.
