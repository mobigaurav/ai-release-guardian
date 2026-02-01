# Phase 2 - AI Release Guardian Auto-QA Guide

## Overview

Phase 2 transforms AI Release Guardian from a **test generation system** into a **fully automated QA pipeline** that executes tests, validates them against acceptance criteria, and makes deployment decisions.

**Vision:** Completely eliminate manual QA testing by automating test execution, validation, and deployment gating.

## Architecture

### Phase 2 Agents

```
PR Pushed
    ↓
[Phase 1: Test Generation + Risk Scoring]
    ↓ (Test definitions)
[Phase 2: Test Execution] ← Runs pytest, captures results
    ↓
[Phase 2: Test Validation] ← Validates AC coverage ≥80%
    ↓
[Phase 2: Deployment Decision] ← GO/GATE/NO-GO
    ↓
└─→ GO: Auto-merge + deploy
└─→ GATE: Manual gate required (DBA, manual testing)
└─→ NO-GO: Blocked, requires fixes
```

### Four New Agents

#### 1. **Test Execution Agent** (`test_executor.py`)
- **Purpose:** Executes generated tests using pytest
- **Input:** Repository path, test pattern
- **Output:** Structured test results with pass/fail status
- **Key Methods:**
  - `execute_tests()` - runs pytest with JSON reporting
  - `run_unit_tests()` - runs only unit tests
  - `run_integration_tests()` - runs only integration tests
  - `run_e2e_tests()` - runs end-to-end tests

**Example Output:**
```json
{
  "status": "SUCCESS",
  "summary": {
    "total": 45,
    "passed": 42,
    "failed": 2,
    "errors": 1,
    "skipped": 0,
    "pass_rate": 93.33,
    "execution_time": 45.2,
    "timestamp": "2024-01-15T10:30:45.123Z"
  },
  "tests": [
    {
      "name": "test_login_success",
      "status": "PASSED",
      "duration": 0.45
    },
    {
      "name": "test_database_migration",
      "status": "FAILED",
      "duration": 2.1,
      "message": "Connection timeout"
    }
  ]
}
```

#### 2. **Test Validation Agent** (`test_validator.py`)
- **Purpose:** Validates test coverage against acceptance criteria
- **Input:** Test results, AC from Jira, coverage requirement (default 80%)
- **Output:** Validation report with coverage %, gaps identified
- **Key Methods:**
  - `validate_tests()` - validates AC coverage
  - `check_coverage_gaps()` - identifies untested AC
  - `validate_test_assertions()` - checks test quality

**Example Output:**
```json
{
  "status": "PASS",
  "coverage_percentage": 92,
  "total_ac": 50,
  "covered_ac": 46,
  "gaps": [
    "AC-123: User logout with active sessions",
    "AC-456: Export data to CSV format"
  ],
  "coverage_by_type": {
    "integration": 95,
    "unit": 88,
    "e2e": 90
  }
}
```

#### 3. **Deployment Decision Agent** (`deployment_decider.py`)
- **Purpose:** Makes GO/GATE/NO-GO decisions based on test results
- **Input:** Test results, validation report, risk assessment
- **Output:** Decision with confidence, reasoning, gates, recommendations
- **Key Methods:**
  - `make_decision()` - evaluates all criteria and decides
  - `can_auto_merge()` - checks if PR can auto-merge
  - `format_decision_summary()` - creates human-readable summary

**Decision Logic (7-tier):**
1. **Tests FAILED** → **NO-GO** (blocker)
2. **AC coverage < 80%** → **NO-GO** (blocker)
3. **Validation failed** → **NO-GO** (blocker)
4. **Risk ≥75 (CRITICAL)** → **NO-GO** (requires extensive review)
5. **Risk ≥50 + DB changes** → **GATE** (DBA approval required)
6. **Risk ≥50 other changes** → **GATE** (manual testing recommended)
7. **All criteria pass** → **GO** (confidence = pass_rate × coverage)

**Example Output:**
```json
{
  "status": "GATE",
  "confidence": 78,
  "deployment_gates": [
    "DBA_REVIEW: Database schema changes detected",
    "MANUAL_TESTING: Risk score 68/100 - high risk area"
  ],
  "reasoning": [
    "45/45 tests passed (100%)",
    "92% AC coverage ≥80% threshold",
    "Risk score 68/100 (HIGH) - requires manual testing",
    "Database schema changes detected - needs DBA review"
  ],
  "recommendation": "Deploy to staging for manual QA testing. Require DBA sign-off before production deployment.",
  "next_steps": [
    "1. Request DBA review of schema changes",
    "2. Run manual testing in staging environment",
    "3. Verify no data migration issues",
    "4. Get DBA approval before production"
  ]
}
```

#### 4. **Phase 2 Orchestrator** (`phase2_orchestrator.py`)
- **Purpose:** Orchestrates all Phase 1 & Phase 2 agents into a cohesive pipeline
- **Interface:** CLI tool with subcommands and Python API
- **Key Methods:**
  - `generate_tests()` - Phase 1: test generation + risk scoring
  - `execute_tests()` - Phase 2: runs pytest
  - `validate_tests()` - Phase 2: validates AC coverage
  - `make_decision()` - Phase 2: deployment decision
  - `end_to_end()` - complete Phase 1 + Phase 2 pipeline

## Running Phase 2

### Option 1: GitHub Actions Workflow (Recommended)

The workflow automatically runs on every PR:

```yaml
# Triggers on:
# - PR opened/updated/reopened
# - Push to main/develop

# Jobs (sequential):
# 1. phase1-test-generation: Generate tests + score risk
# 2. phase2-execute-tests: Run pytest
# 3. phase2-validate-tests: Check AC coverage
# 4. phase2-deployment-decision: Make GO/GATE/NO-GO decision
# 5. publish-results: Display summary
```

**Result:** PR comment with full decision and next steps

### Option 2: CLI - End-to-End Pipeline

Run the complete Phase 1 + Phase 2 pipeline locally:

```bash
# Full pipeline
python -m src.agents.phase2_orchestrator end-to-end \
  --repo-owner "my-org" \
  --repo-name "my-repo" \
  --pr-number 123 \
  --repo-path . \
  --output-dir ./results

# Creates 4 JSON files:
# 1. results/tests_generated.json (Phase 1)
# 2. results/tests_executed.json (Phase 2)
# 3. results/tests_validated.json (Phase 2)
# 4. results/deployment_decision.json (Phase 2)
```

### Option 3: CLI - Individual Steps

Run each phase separately:

```bash
# Phase 1: Generate tests
python -m src.agents.phase2_orchestrator generate-tests \
  --repo-owner "my-org" \
  --repo-name "my-repo" \
  --pr-number 123 \
  --output tests_generated.json

# Phase 2: Execute tests
python -m src.agents.phase2_orchestrator execute-tests \
  --repo-path . \
  --output tests_executed.json

# Phase 2: Validate tests
python -m src.agents.phase2_orchestrator validate-tests \
  --repo-owner "my-org" \
  --repo-name "my-repo" \
  --pr-number 123 \
  --test-results tests_executed.json \
  --output tests_validated.json

# Phase 2: Make decision
python -m src.agents.phase2_orchestrator make-decision \
  --test-defs tests_generated.json \
  --test-results tests_executed.json \
  --validation tests_validated.json \
  --output deployment_decision.json
```

### Option 4: Python API

Use the orchestrator directly in code:

```python
from src.agents import create_phase2_orchestrator

orchestrator = create_phase2_orchestrator()

# Full pipeline
results = orchestrator.end_to_end(
    repo_owner="my-org",
    repo_name="my-repo",
    pr_number=123,
    repo_path=".",
    output_dir="./results"
)

print(f"Decision: {results['deployment_decision']['status']}")
print(f"Confidence: {results['deployment_decision']['confidence']}%")
```

## Environment Variables

Required for Phase 2:

```bash
# GitHub
GITHUB_TOKEN=ghp_xxxxxxxxxxxxx

# Jira (optional, needed for AC validation)
JIRA_API_TOKEN=your-api-token
JIRA_DOMAIN=your-domain.atlassian.net
JIRA_PROJECT_KEY=ABC

# Claude AI
CLAUDE_API_KEY=sk-ant-xxxxxxxxxxxxx
```

## Decision Outcomes

### GO ✅
**Confidence:** 70-100%
- All tests passed
- AC coverage ≥80%
- Risk score <50 or mitigated
- **Result:** Auto-merge enabled, deploy to production

**Example:**
```json
{
  "status": "GO",
  "confidence": 95,
  "deployment_gates": [],
  "recommendation": "Deployment approved. Ready for production release.",
  "next_steps": [
    "Auto-merge PR",
    "Deploy to production",
    "Monitor for regressions"
  ]
}
```

### GATE ⚠️
**Confidence:** 40-70%
- Tests passed but risk identified
- AC coverage adequate but gaps exist
- Risk score ≥50 or specific dependencies
- **Result:** Requires approval before deployment

**Gates Examples:**
- `DBA_REVIEW`: Database schema changes
- `SECURITY_REVIEW`: Authentication/authorization changes
- `MANUAL_TESTING`: High-risk area requiring manual verification
- `PERFORMANCE_TEST`: Changes affecting latency/throughput

**Result:** PR comment with required gates. Team must approve gates before deployment.

### NO-GO ❌
**Confidence:** 0-40%
- Tests failed or validation failed
- AC coverage <80%
- Risk score ≥75 (CRITICAL)
- **Result:** Deployment blocked

**Reasons for NO-GO:**
- Critical test failures
- Insufficient AC coverage
- Critical risk detected
- Incompatible changes

**Result:** PR comment with failures. Developer must fix issues and push new commit to retry.

## Metrics & Reporting

Phase 2 provides comprehensive metrics:

### Test Execution Metrics
- **Total tests:** Number of tests generated and executed
- **Pass rate:** Percentage of tests that passed
- **Execution time:** Total time to run all tests
- **Coverage by type:** Unit, integration, E2E breakdown

### Validation Metrics
- **AC coverage:** Percentage of acceptance criteria covered by tests
- **Coverage gaps:** AC not covered by any test
- **Coverage by type:** Unit, integration, E2E breakdown

### Risk Metrics
- **Risk score:** 0-100 (0=low, 100=critical)
- **Risk flags:** Specific high-risk patterns detected
- **Mitigation steps:** Actions to reduce risk

### Decision Metrics
- **Confidence:** 0-100% confidence in decision
- **Decision distribution:** GO/GATE/NO-GO statistics over time

## Best Practices

### 1. Optimize Test Generation
- Keep test scenarios focused and specific
- Avoid duplicative test coverage
- Include edge cases and error scenarios
- Target 80-90% AC coverage (sweet spot)

### 2. Optimize Test Execution
- Run tests in parallel where possible
- Cache dependencies between test runs
- Use test fixtures for common setup
- Keep test runtime under 5 minutes

### 3. Handle GATE Decisions
- Define clear gate approval workflows
- Automate gate approvals where possible (e.g., automated DBA checks)
- Track gate approval times to identify bottlenecks
- Consider auto-merging low-risk GATE decisions

### 4. Monitor NO-GO Decisions
- Track NO-GO reasons to identify patterns
- Work with teams to reduce CRITICAL risk
- Improve test coverage where gaps appear
- Refine decision logic based on outcomes

### 5. Continuous Improvement
- Measure QA velocity: time from PR to deployment
- Track quality metrics: bugs found in production
- Analyze decision accuracy: comparing AI decision vs actual outcomes
- Iterate on decision thresholds based on team's risk tolerance

## Integration with Existing Systems

### GitHub
- Creates PR comments with decision and next steps
- Auto-merges PRs when GO decision reached
- Blocks merge when NO-GO
- Waits for approvals when GATE

### Jira
- Extracts AC from linked Jira tickets
- Links test results back to AC
- Updates AC coverage status
- Tracks test metrics over time

### Slack (Optional)
- Notify team of Phase 2 decisions
- Post deployment decisions
- Alert on recurring NO-GO patterns
- Share QA velocity metrics

### AWS Lambda (Optional)
- Deploy MCP server as Lambda function
- Expose Phase 2 agents via HTTP API
- Integrate with external systems
- Scale to handle multiple repos

## Troubleshooting

### Tests Not Executing
**Problem:** Phase 2 executor shows no tests run

**Solutions:**
1. Check test file naming: must match `test_*.py` pattern
2. Verify pytest is installed: `pytest --version`
3. Check repo path is correct
4. Ensure tests import successfully: `pytest --collect-only`

### Low AC Coverage
**Problem:** Validation shows <80% AC coverage

**Solutions:**
1. Generate more test scenarios in Phase 1
2. Ensure AC is specific and testable
3. Add missing AC to test generation logic
4. Review gaps identified in validation report

### High Risk Score
**Problem:** Risk score ≥75 causing NO-GO decision

**Solutions:**
1. Reduce scope of changes
2. Add more regression tests
3. Perform manual risk assessment
4. Implement mitigations and re-test

### Workflow Timeout
**Problem:** GitHub Actions workflow exceeds time limits

**Solutions:**
1. Increase timeout in workflow YAML
2. Parallelize test execution
3. Filter tests to only modified modules
4. Cache dependencies more aggressively

## Measuring Success

Phase 2 success metrics:

| Metric | Target | Measurement |
|--------|--------|-------------|
| QA Velocity | -80% time | Time from PR to deployment |
| Test Coverage | 80-90% | AC coverage in validation |
| Automation Rate | 95%+ | Percentage of PRs auto-merged |
| Zero Manual Testing | 99%+ | Manual QA time eliminated |
| Decision Accuracy | 99%+ | AI decisions matching real outcomes |
| NO-GO Avoidance | <5% | Percentage of NO-GO decisions |

## Next Steps

### Immediate (Week 1)
- ✅ Deploy Phase 2 agents
- ✅ Test on ai-release-guardian repo
- ✅ Iterate on decision logic
- ✅ Train team on GATE workflows

### Short-term (Month 1)
- Measure QA velocity improvement
- Collect AI decision accuracy metrics
- Refine risk scoring based on outcomes
- Integrate with Slack for notifications

### Long-term (Quarter 1)
- Expand to all repositories
- Integrate with AWS Lambda
- Add performance test automation
- Build dashboard for QA metrics

## Support & Questions

For issues or questions:
1. Check [troubleshooting section](#troubleshooting)
2. Review agent documentation in code
3. Check GitHub Actions logs in PR
4. Contact AI Release Guardian maintainers
