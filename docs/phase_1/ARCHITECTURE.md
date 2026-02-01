# Architecture - AI Release Guardian

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        GitHub Repository                        │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Pull Request (opened/synchronized)                     │   │
│  │  - Code diff                                             │   │
│  │  - PR title & description                               │   │
│  │  - Jira ticket references (e.g., PROJ-123)              │   │
│  └──────────────┬───────────────────────────────────────────┘   │
└─────────────────┼──────────────────────────────────────────────┘
                  │ GitHub Webhook (HTTP POST)
                  │
        ┌─────────▼──────────┐
        │  GitHub Webhook    │
        │  (Payload delivery)│
        └─────────┬──────────┘
                  │
    ┌─────────────▼─────────────────┐
    │    AWS API Gateway            │
    │    (Webhook endpoint)         │
    │    /webhook (POST)            │
    └─────────────┬─────────────────┘
                  │
    ┌─────────────▼─────────────────┐
    │    AWS Lambda                 │
    │  ai-release-guardian          │
    │  (Event handler)              │
    │                               │
    │  - Parse webhook              │
    │  - Extract context            │
    │  - Call MCP methods           │
    │  - Format & post comment      │
    └─────────────┬─────────────────┘
                  │
                  │ Calls (same Lambda or separate service)
                  │
    ┌─────────────▼───────────────────────────────────────────┐
    │         MCP Server (Release Guardian)                   │
    │  (Can run as separate service or embedded in Lambda)    │
    │                                                         │
    │  ┌──────────────────────────────────────────────────┐  │
    │  │ Planner Agent                                    │  │
    │  │ - Reads PR diff                                  │  │
    │  │ - Extracts Jira AC                               │  │
    │  │ - Classifies files (backend, frontend, DB, etc)  │  │
    │  │ - Detects risky patterns                         │  │
    │  └──────────────────────────────────────────────────┘  │
    │                      ↓                                 │
    │  ┌──────────────────────────────────────────────────┐  │
    │  │ Test Generator Agent                             │  │
    │  │ - Calls Claude API                               │  │
    │  │ - Generates integration tests                    │  │
    │  │ - Generates automation tests                     │  │
    │  │ - Generates E2E flows                            │  │
    │  │ - Prioritizes by risk                            │  │
    │  └──────────────────────────────────────────────────┘  │
    │                      ↓                                 │
    │  ┌──────────────────────────────────────────────────┐  │
    │  │ Risk Scorer Agent                                │  │
    │  │ - Analyzes change magnitude                      │  │
    │  │ - Identifies risky patterns                      │  │
    │  │ - Calls Claude for risk assessment               │  │
    │  │ - Returns risk score (0-100)                     │  │
    │  │ - Suggests mitigation steps                      │  │
    │  └──────────────────────────────────────────────────┘  │
    │                      ↓                                 │
    │  ┌──────────────────────────────────────────────────┐  │
    │  │ Rollback Planner Agent                           │  │
    │  │ - Generates step-by-step rollback               │  │
    │  │ - Identifies critical checks                     │  │
    │  │ - Estimates rollback time                        │  │
    │  │ - Creates pre/post deployment checklists         │  │
    │  └──────────────────────────────────────────────────┘  │
    │                      ↓                                 │
    │  ┌──────────────────────────────────────────────────┐  │
    │  │ Integrations                                     │  │
    │  │ ├─ GitHub API (fetch PR, post comment)           │  │
    │  │ ├─ Jira API (fetch AC)                           │  │
    │  │ └─ Claude API (AI analysis)                      │  │
    │  └──────────────────────────────────────────────────┘  │
    └─────────────┬───────────────────────────────────────────┘
                  │
                  │ Result: PR Comment JSON
                  │
    ┌─────────────▼──────────────┐
    │  GitHub PR Comment API     │
    │  (Post comment on PR)      │
    │  /repos/{owner}/{repo}/    │
    │   issues/{pr}/comments     │
    └─────────────┬──────────────┘
                  │
        ┌─────────▼──────────┐
        │  PR Comment        │
        │  (Posted & visible)│
        │                    │
        │  ✓ Test scenarios  │
        │  ✓ Risk score      │
        │  ✓ Recommendations │
        │  ✓ Rollback plan   │
        └────────────────────┘
```

## Data Flow

### Input
```
GitHub Webhook Payload
├── PR Number
├── Repository (owner/name)
├── PR Title
├── PR Body (description)
├── Files Changed (with diffs)
└── Author
```

### Processing Pipeline

```
1. Parse Webhook
   ↓
2. Extract Jira Tickets from PR title/body
   (e.g., PROJ-123, INFRA-45)
   ↓
3. Fetch PR Diff from GitHub API
   ├── File names & changes
   ├── Patch content
   └── Additions/deletions
   ↓
4. Fetch Jira Ticket Details (optional)
   ├── Acceptance Criteria
   ├── Ticket type
   ├── Priority
   └── Status
   ↓
5. Planner Agent
   ├── Classify files by type
   ├── Detect risky patterns
   └── Prepare context for analysis
   ↓
6. Claude API Call #1 (PR Analysis)
   Input: PR diff + AC + file types
   Output: Key changes, integration points, risks
   ↓
7. Claude API Call #2 (Test Generation)
   Input: Code diff + AC + file classification
   Output: Integration, automation, E2E test scenarios
   ↓
8. Claude API Call #3 (Risk Scoring)
   Input: Changes summary + file types + magnitude
   Output: Risk score, confidence %, flags, recommendations
   ↓
9. Aggregate Results
   ├── Test scenarios
   ├── Risk assessment
   ├── Recommendations
   └── Rollback plan
   ↓
10. Format PR Comment
    (Markdown with badges, sections, highlights)
    ↓
11. Post Comment to PR
    (GitHub API)
```

### Output

```json
{
  "pr_comment": {
    "title": "🤖 AI Release Guardian Analysis",
    "sections": [
      {
        "title": "🧪 Auto-Generated Test Scenarios",
        "integration_tests": [
          {
            "id": "integration_1",
            "name": "test_user_creation",
            "description": "...",
            "steps": [...],
            "priority": "high"
          }
        ],
        "automation_tests": [...],
        "e2e_flows": [...]
      },
      {
        "title": "🟡 Release Risk Assessment",
        "risk_score": 35,
        "confidence": 65,
        "risk_flags": [...],
        "requires_manual_review": false
      },
      {
        "title": "📋 Linked Jira Tickets",
        "tickets": ["PROJ-123"]
      },
      {
        "title": "💡 Recommendations",
        "suggestions": [...]
      }
    ]
  }
}
```

## Agent Responsibilities

### 1. Planner Agent
**Input:** PR diff, PR metadata (title, body)
**Output:** Structured context

**Process:**
```
Parse PR
  ├─ Extract Jira tickets (regex: [A-Z]+-[0-9]+)
  ├─ Fetch Jira AC (if available)
  ├─ Classify files:
  │   ├─ Backend (Python, Go, JS, etc)
  │   ├─ Frontend (JS, React, Vue, etc)
  │   ├─ Database (SQL, migrations)
  │   ├─ Infrastructure (Terraform, k8s)
  │   ├─ Config (YAML, JSON)
  │   └─ Tests (test files)
  ├─ Extract risky patterns:
  │   ├─ Database changes → migration risk
  │   ├─ Auth changes → security review needed
  │   ├─ API changes → contract compatibility
  │   └─ Infrastructure → DevOps review
  └─ Calculate change magnitude
```

### 2. Test Generator Agent
**Input:** Code diff, AC, file types
**Output:** Test scenarios (integration, automation, E2E)

**Process:**
```
Call Claude:
  "Generate tests for these changes against these AC"
  
Claude returns:
  ├─ Integration tests
  │   └─ (service-to-service interactions)
  ├─ Automation tests
  │   └─ (API endpoint flows)
  ├─ E2E flows
  │   └─ (full user journeys)
  
Convert to TestScenario objects:
  ├─ test_id
  ├─ name
  ├─ description
  ├─ steps
  ├─ expected_outcomes
  └─ priority

Sort by priority (high → medium → low)
```

### 3. Risk Scorer Agent
**Input:** Change summary, file types, magnitude, risky patterns
**Output:** Risk score (0-100), confidence %, recommendations

**Process:**
```
Static Analysis:
  ├─ Database changes? → +25 risk
  ├─ Auth changes? → +30 risk
  ├─ API breaking changes? → +20 risk
  ├─ Infrastructure? → +20 risk
  └─ Large change (>500 lines)? → +10 risk

Call Claude:
  "Score deployment risk for this change"
  
Claude returns:
  ├─ risk_score (0-100)
  ├─ confidence_percentage (inverse of risk)
  ├─ risk_factors
  ├─ recommendations
  └─ deployment_gates

Aggregate scoring
```

### 4. Rollback Planner Agent
**Input:** Release ID, changed files, file types, risk flags
**Output:** Step-by-step rollback procedure

**Process:**
```
Generate steps based on file types:
  
If database changes:
  ├─ Backup recent DB
  ├─ Revert schema
  ├─ Validate data integrity
  └─ Verify constraints
  
If backend changes:
  ├─ Deploy previous version
  ├─ Clear caches
  ├─ Health checks
  └─ Monitor errors
  
If frontend changes:
  ├─ Clear CDN
  ├─ Deploy previous version
  └─ Cross-browser verification
  
If infrastructure:
  ├─ Restore previous config
  ├─ DNS failover
  └─ Traffic reroute

Add monitoring:
  ├─ 30-minute post-rollback monitoring
  ├─ Error rate validation
  └─ Performance baseline check

Estimate duration based on complexity
```

## Integration Points

### GitHub API
```
GET /repos/{owner}/{repo}/pulls/{pr}/files
  ↓ Fetch PR files with diff

GET /repos/{owner}/{repo}/pulls/{pr}
  ↓ Fetch PR metadata (title, body)

POST /repos/{owner}/{repo}/issues/{pr}/comments
  ↓ Post analysis comment
```

### Jira API
```
GET /rest/api/3/issues/{key}
  ↓ Fetch ticket details, acceptance criteria
```

### Claude API
```
POST /messages
  ↓ Call Claude for:
     - PR analysis
     - Test generation
     - Risk scoring
```

## Data Models

### TestScenario
```python
{
  test_id: str              # "integration_1"
  name: str                 # "test_user_creation"
  description: str
  type: str                 # "integration_test" | "automation_test" | "e2e_test"
  scenario_steps: [str]     # ["POST /users", "Query DB"]
  expected_outcomes: [str]  # ["User created", "Email sent"]
  priority: str             # "high" | "medium" | "low"
  risk_flags: [str]         # ["async_dependency", ...]
}
```

### RiskAssessment
```python
{
  risk_score: float         # 0-100
  confidence_percentage: float  # 0-100
  risk_flags: [str]         # ["DB migration", "Auth change"]
  suggestions: [str]        # ["Run tests", "Manual review"]
  requires_manual_review: bool
}
```

### PRAnalysis
```python
{
  pr_number: int
  pr_title: str
  repo: str
  changed_files: [str]
  jira_tickets: [str]
  acceptance_criteria: [str]
  test_scenarios: [TestScenario]
  risk_assessment: RiskAssessment
  summary: str
}
```

## Performance Characteristics

| Metric | Value | Notes |
|--------|-------|-------|
| Lambda Timeout | 60s | Including API calls |
| Claude API Time | 15-30s | Depends on input size |
| Memory Required | 512 MB | Sufficient for analysis |
| Cold Start | 5-10s | First invocation |
| Warm Start | <1s | Subsequent invocations |
| GitHub API Calls | 2-4 | Get PR, fetch AC, post comment |
| Jira API Calls | 1-3 | Fetch tickets (if available) |
| Claude API Calls | 3 | PR analysis, tests, risk |

## Security Architecture

```
GitHub Webhook
     ↓
   (HTTPS)
     ↓
API Gateway (AWS)
     ↓ (Secured with API Key or OAuth)
Lambda Function
     ↓
Environment Variables (not in code):
  ├─ GITHUB_TOKEN
  ├─ JIRA_API_TOKEN
  ├─ CLAUDE_API_KEY
     ↓
External API Calls (HTTPS encrypted):
  ├─ GitHub API
  ├─ Jira API
  ├─ Claude API
     ↓
IAM Policies:
  └─ Lambda execution role (minimal permissions)
```

## Scalability

### Single Lambda
- ✅ Works for 1-50 PRs/day per repo
- ✅ Suitable for Phase 1

### Multi-Lambda (Future)
- Queue-based processing
- Parallel test/risk analysis
- Dedicated consumer Lambda

### Multi-Repo
- Single Lambda handles multiple repos
- Webhook routing logic
- Per-repo configuration

---

**See QUICK_REFERENCE.md for code examples and API usage.**
