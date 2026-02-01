# Phase 2 Quick Reference

## Commands Cheat Sheet

### End-to-End Pipeline
```bash
# Run complete Phase 1 + Phase 2 pipeline
python -m src.agents.phase2_orchestrator end-to-end \
  --repo-owner "org" \
  --repo-name "repo" \
  --pr-number 123 \
  --repo-path . \
  --output-dir ./results
```

### Individual Phases
```bash
# Phase 1: Generate tests + score risk
python -m src.agents.phase2_orchestrator generate-tests \
  --repo-owner "org" \
  --repo-name "repo" \
  --pr-number 123 \
  --output tests_generated.json

# Phase 2a: Execute tests
python -m src.agents.phase2_orchestrator execute-tests \
  --repo-path . \
  --output tests_executed.json

# Phase 2b: Validate tests
python -m src.agents.phase2_orchestrator validate-tests \
  --repo-owner "org" \
  --repo-name "repo" \
  --pr-number 123 \
  --test-results tests_executed.json \
  --output tests_validated.json

# Phase 2c: Make decision
python -m src.agents.phase2_orchestrator make-decision \
  --test-defs tests_generated.json \
  --test-results tests_executed.json \
  --validation tests_validated.json \
  --output deployment_decision.json
```

## Python API Examples

### Load Phase 2 Agents
```python
from src.agents import (
    create_phase2_orchestrator,
    create_test_executor_agent,
    create_test_validator_agent,
    create_deployment_decision_agent
)

# Orchestrator (recommended - all-in-one)
orchestrator = create_phase2_orchestrator()

# Individual agents
executor = create_test_executor_agent()
validator = create_test_validator_agent()
decider = create_deployment_decision_agent()
```

### Execute Tests
```python
from src.agents import create_test_executor_agent

executor = create_test_executor_agent()

# Run all tests
results = executor.execute_tests(repo_path=".")

# Run specific test types
unit_results = executor.run_unit_tests()
integration_results = executor.run_integration_tests()
e2e_results = executor.run_e2e_tests()

# Check results
print(f"Pass rate: {results['summary']['pass_rate']}%")
print(f"Total tests: {results['summary']['total']}")
```

### Validate Against AC
```python
from src.agents import create_test_validator_agent

validator = create_test_validator_agent()

validation = validator.validate_tests(
    test_results=test_results,
    acceptance_criteria=ac_from_jira,
    coverage_requirement=0.80  # 80% minimum
)

print(f"Coverage: {validation['coverage_percentage']}%")
print(f"Status: {validation['status']}")
print(f"Gaps: {validation['gaps']}")
```

### Make Deployment Decision
```python
from src.agents import create_deployment_decision_agent

decider = create_deployment_decision_agent()

decision = decider.make_decision(
    test_results=test_results,
    validation_report=validation,
    risk_assessment=risk_score
)

print(f"Decision: {decision['status']}")  # GO, GATE, or NO-GO
print(f"Confidence: {decision['confidence']}%")
print(f"Reasoning: {decision['reasoning']}")
```

### Full Pipeline
```python
from src.agents import create_phase2_orchestrator

orchestrator = create_phase2_orchestrator()

results = orchestrator.end_to_end(
    repo_owner="org",
    repo_name="repo",
    pr_number=123,
    repo_path=".",
    output_dir="./results"
)

# Access results
print(f"Tests generated: {results['tests_generated']['tests']['total']}")
print(f"Tests passed: {results['tests_executed']['summary']['pass_rate']}%")
print(f"AC coverage: {results['tests_validated']['coverage_percentage']}%")
print(f"Decision: {results['deployment_decision']['status']}")
```

## Environment Setup

### Required Environment Variables
```bash
# Create .env or export
export GITHUB_TOKEN="ghp_xxxxxxxxxxxxx"
export CLAUDE_API_KEY="sk-ant-xxxxxxxxxxxxx"
export JIRA_API_TOKEN="your-api-token"  # Optional
export JIRA_DOMAIN="your-domain.atlassian.net"  # Optional
```

### Load Environment
```bash
# From .env file
source .env

# Or inline
export CLAUDE_API_KEY="sk-ant-xxxxxxxxxxxxx" && python -m src.agents.phase2_orchestrator end-to-end ...
```

## Decision Logic Quick Reference

### GO ✅ (Auto-merge enabled)
- All tests PASSED (100% pass rate)
- AC coverage ≥80%
- Risk score <50
- Confidence: 70-100%

### GATE ⚠️ (Manual approval required)
- Tests PASSED but risk detected (≥50)
- AC coverage ≥80% with gaps
- Specific gates required (DBA, security, manual testing)
- Confidence: 40-70%

### NO-GO ❌ (Deployment blocked)
- Tests FAILED or coverage <80%
- Risk score ≥75 (CRITICAL)
- Validation failed
- Confidence: 0-40%

## Output File Format

### deployment_decision.json
```json
{
  "status": "GO|GATE|NO-GO",
  "confidence": 0-100,
  "deployment_gates": [],
  "reasoning": [],
  "recommendation": "string",
  "next_steps": [],
  "timestamp": "ISO-8601"
}
```

### tests_executed.json
```json
{
  "status": "SUCCESS|ERROR",
  "summary": {
    "total": number,
    "passed": number,
    "failed": number,
    "pass_rate": number,
    "execution_time": number
  },
  "tests": [
    {
      "name": "string",
      "status": "PASSED|FAILED|ERROR|SKIPPED",
      "duration": number
    }
  ]
}
```

### tests_validated.json
```json
{
  "status": "PASS|FAIL",
  "coverage_percentage": 0-100,
  "total_ac": number,
  "covered_ac": number,
  "gaps": ["AC-id: description"],
  "coverage_by_type": {
    "integration": number,
    "unit": number,
    "e2e": number
  }
}
```

## Common Workflows

### Debug Failed Deployment
```bash
# 1. Get test results
cat tests_executed.json | grep FAILED

# 2. Check validation gaps
cat tests_validated.json | jq '.gaps'

# 3. Check decision reasoning
cat deployment_decision.json | jq '.reasoning'

# 4. Fix tests and retry
git add -A && git commit -m "Fix: Update tests" && git push
```

### Monitor Workflow Progress
```bash
# Watch GitHub Actions
gh run list --workflow phase2-release-guardian.yml --limit 5

# Get latest run
gh run view --latest --workflow phase2-release-guardian.yml

# Stream logs in real-time
gh run watch <run-id>
```

### Export Metrics
```bash
# Get all decisions from last week
gh run list --workflow phase2-release-guardian.yml \
  --created ">=2024-01-08" \
  --json conclusion,createdAt \
  --jq '.[] | {date: .createdAt, status: .conclusion}'
```

## Troubleshooting Quick Fixes

### Tests Not Running
```bash
# Check pytest is installed
pytest --version

# Verify test files exist
find . -name "test_*.py" -type f

# Run pytest directly
pytest . -v
```

### Low AC Coverage
```bash
# See what's not covered
cat tests_validated.json | jq '.gaps'

# Generate more tests
python -m src.agents.phase2_orchestrator generate-tests \
  --repo-owner "org" --repo-name "repo" --pr-number 123 \
  --output tests_generated.json
```

### High Risk Score
```bash
# See risk details
cat tests_generated.json | jq '.risk_assessment'

# Add mitigations and retry
# Then rerun: python -m src.agents.phase2_orchestrator make-decision ...
```

### Workflow Timeout
```bash
# Increase timeout
# Edit .github/workflows/phase2-release-guardian.yml
# Change timeout-minutes: 10 → 15

# Run pytest in parallel (faster)
# pytest -n auto

# Filter to only necessary tests
pytest --co -q
```

## Links & Documentation

- **Full Phase 2 Guide:** `docs/PHASE2_GUIDE.md`
- **Deployment Guide:** `docs/PHASE2_DEPLOYMENT.md`
- **Architecture:** `docs/ARCHITECTURE.md`
- **GitHub Actions:** https://docs.github.com/actions
- **Pytest Docs:** https://docs.pytest.org/
- **Claude API:** https://docs.anthropic.com/

## Support

- **Issues:** Open GitHub issue in ai-release-guardian
- **Slack:** #ai-release-guardian
- **Email:** team@example.com
