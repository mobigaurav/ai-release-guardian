# Phase 2 Deployment Guide

## Quick Start

### 1. Prerequisites
```bash
# Python 3.11+
python --version

# Git
git --version

# pip
pip --version
```

### 2. Clone & Setup
```bash
cd /path/to/ai-release-guardian

# Install dependencies
pip install -r requirements.txt

# Test installation
python -m pytest --version
pytest --version
python -c "from src.agents import create_phase2_orchestrator; print('✓ Phase 2 ready')"
```

### 3. Configure Environment
```bash
# Create .env file
cat > .env << 'EOF'
# GitHub
GITHUB_TOKEN=ghp_xxxxxxxxxxxxx

# Claude AI
CLAUDE_API_KEY=sk-ant-xxxxxxxxxxxxx

# Jira (optional)
JIRA_API_TOKEN=your-api-token
JIRA_DOMAIN=your-domain.atlassian.net
JIRA_PROJECT_KEY=ABC
EOF

# Load environment
source .env
```

### 4. Test Phase 2 Locally
```bash
# Run end-to-end pipeline
python -m src.agents.phase2_orchestrator end-to-end \
  --repo-owner "my-org" \
  --repo-name "my-repo" \
  --pr-number 1 \
  --repo-path . \
  --output-dir ./results

# Check results
cat results/deployment_decision.json
```

### 5. Deploy to GitHub
```bash
# Push changes to repo
git add .
git commit -m "Phase 2: Add auto-QA pipeline"
git push origin main

# GitHub Actions automatically triggers on PR
# Check Actions tab to see workflow execution
```

## GitHub Actions Deployment

### Automatic Setup (Recommended)

The workflow file is already created at `.github/workflows/phase2-release-guardian.yml`

**What it does:**
1. On every PR, Phase 1 generates tests + scores risk
2. Phase 2 executor runs all tests
3. Phase 2 validator checks AC coverage
4. Phase 2 decider makes GO/GATE/NO-GO decision
5. Posts decision as PR comment
6. Auto-merges if GO

**To activate:**
```bash
# Just push the code - workflow auto-triggers on PR
git push origin feature/my-feature

# Check Actions tab to see workflow running
# PR comment will appear automatically with decision
```

### Manual Workflow Triggers

If needed, manually trigger the workflow:

```bash
# Using GitHub CLI
gh workflow run phase2-release-guardian.yml

# Or push to trigger branch
git push origin develop
```

### Monitor Workflow

**In GitHub UI:**
1. Go to repo → Actions tab
2. Click "Phase 2 - Release Guardian Auto-QA"
3. See job status in real-time:
   - Phase 1: Generate Tests & Score Risk
   - Phase 2: Execute Tests
   - Phase 2: Validate Tests
   - Phase 2: Deployment Decision
   - Publish Results

**Get artifacts:**
```bash
# Download after workflow completes
gh run download <run-id> -D ./results

# Or check PR for direct download link
```

### Debugging Workflow

**Check logs:**
```bash
# Using GitHub CLI
gh run view <run-id> --log

# Or in UI: Click job → See output
```

**Common issues:**
- **YAML syntax error:** Validate with `yamllint .github/workflows/*.yml`
- **Env vars not set:** Check repository secrets
- **Timeout:** Increase timeout in workflow YAML (default 300s)
- **pytest not found:** Verify `pip install -r requirements.txt` runs

## Environment Variables & Secrets

### Required GitHub Secrets

Set these in GitHub repo settings (Settings → Secrets and variables → Actions):

```bash
# GitHub Token (for API calls)
GITHUB_TOKEN # Auto-provided by GitHub Actions

# Claude AI API Key
CLAUDE_API_KEY # Get from https://console.anthropic.com/keys

# Jira API Token (optional)
JIRA_API_TOKEN # Get from https://id.atlassian.com/manage-profile/security

# Test Configuration (optional)
TEST_COVERAGE_THRESHOLD=80  # Default: 80%
TEST_TIMEOUT_SECONDS=300    # Default: 300
```

### Set Secrets via CLI

```bash
# Using GitHub CLI
gh secret set CLAUDE_API_KEY --body "sk-ant-xxxxxxxxxxxxx"
gh secret set JIRA_API_TOKEN --body "your-api-token"

# Or via UI: Settings → Secrets → New repository secret
```

### Verify Secrets

```bash
# List all secrets
gh secret list

# Or in UI: Settings → Secrets (masked)
```

## Testing Phase 2

### Test on ai-release-guardian Itself

Since ai-release-guardian is the system itself, we "dogfood" it:

```bash
# 1. Create a feature branch
git checkout -b test/phase2-deployment

# 2. Add a test file to trigger Phase 2
cat > tests/test_phase2_agents.py << 'EOF'
"""Test Phase 2 agents"""
import pytest
from src.agents import create_phase2_orchestrator

def test_orchestrator_initialization():
    """Test orchestrator can be initialized"""
    orchestrator = create_phase2_orchestrator()
    assert orchestrator is not None

def test_test_executor_available():
    """Test executor is available"""
    from src.agents import create_test_executor_agent
    executor = create_test_executor_agent()
    assert executor is not None

def test_test_validator_available():
    """Test validator is available"""
    from src.agents import create_test_validator_agent
    validator = create_test_validator_agent()
    assert validator is not None

def test_deployment_decider_available():
    """Test decider is available"""
    from src.agents import create_deployment_decision_agent
    decider = create_deployment_decision_agent()
    assert decider is not None
EOF

# 3. Push and open PR
git add -A
git commit -m "Test: Add Phase 2 dogfood tests"
git push origin test/phase2-deployment

# 4. Open PR on GitHub
# Go to https://github.com/your-org/ai-release-guardian
# Create PR from test/phase2-deployment → main

# 5. Watch workflow execute
# Check Actions tab to see all Phase 2 jobs
# Verify PR comment with decision

# 6. If GO decision reached, merge
git checkout main
git merge test/phase2-deployment
```

### Run Tests Locally

```bash
# Execute Phase 2 agents locally
python -m pytest tests/test_phase2_agents.py -v

# Run end-to-end test
python -m src.agents.phase2_orchestrator end-to-end \
  --repo-owner "your-org" \
  --repo-name "ai-release-guardian" \
  --pr-number 1 \
  --repo-path . \
  --output-dir ./test_results

# Check results
cat test_results/deployment_decision.json | python -m json.tool
```

## Troubleshooting Deployment

### Workflow Won't Trigger

**Problem:** Workflow file is present but not showing in Actions tab

**Solutions:**
1. Verify workflow file at `.github/workflows/phase2-release-guardian.yml`
2. Ensure workflow YAML is valid:
   ```bash
   python -c "import yaml; yaml.safe_load(open('.github/workflows/phase2-release-guardian.yml'))"
   ```
3. Workflow only triggers on PR with configured triggers
4. Force workflow update:
   ```bash
   git add .github/workflows/phase2-release-guardian.yml
   git commit --amend
   git push --force-with-lease
   ```

### Missing Secrets

**Problem:** Job fails with "secret not available"

**Solutions:**
1. Verify secrets are set:
   ```bash
   gh secret list
   ```
2. Add missing secrets:
   ```bash
   gh secret set CLAUDE_API_KEY --body "your-key"
   ```
3. Environment variable names must match exactly in workflow

### Test Execution Timeout

**Problem:** Workflow times out during test execution

**Solutions:**
1. Increase timeout in workflow YAML:
   ```yaml
   - name: Phase 2 - Execute Tests
     timeout-minutes: 15  # Change from default 10
   ```
2. Optimize tests:
   - Remove slow tests temporarily
   - Run only critical tests
   - Use test markers: `pytest -m "not slow"`
3. Use parallel execution:
   ```bash
   pytest -n auto  # Requires pytest-xdist
   ```

### Python Version Mismatch

**Problem:** Tests fail with "ModuleNotFoundError" or version errors

**Solutions:**
1. Verify Python version in workflow matches requirements:
   ```yaml
   python-version: '3.11'  # Match requirements
   ```
2. Verify all dependencies are in requirements.txt:
   ```bash
   pip freeze > requirements.txt
   ```
3. Clear pip cache:
   ```bash
   pip cache purge
   ```

### API Authentication Failures

**Problem:** Workflow fails with authentication errors

**Solutions:**
1. Verify tokens are correct:
   ```bash
   # GitHub Token
   echo $GITHUB_TOKEN | cut -c1-20
   
   # Claude API Key
   echo $CLAUDE_API_KEY | cut -c1-20
   ```
2. Check token expiration:
   - GitHub: https://github.com/settings/tokens
   - Claude: https://console.anthropic.com/keys
   - Jira: https://id.atlassian.com/manage-profile/security
3. Rotate expired tokens:
   ```bash
   gh secret set CLAUDE_API_KEY --body "new-key"
   ```

## Performance Tuning

### Speed Up Workflow

**Parallel Execution:**
```yaml
# Run multiple jobs in parallel
  phase2-execute-tests:
    runs-on: ubuntu-latest
    parallelization: 4  # Run 4 test suites in parallel
```

**Cache Dependencies:**
```yaml
- name: Cache pip packages
  uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
```

**Optimize Pytest:**
```bash
# Run tests in parallel (requires pytest-xdist)
pytest -n auto --dist loadscope
```

### Reduce Workflow Time

Current typical times:
- Phase 1 (Generate tests): 30-60 seconds
- Phase 2 (Execute tests): 60-120 seconds
- Phase 2 (Validate tests): 10-20 seconds
- Phase 2 (Deployment decision): 5-10 seconds
- **Total: ~2-3 minutes per PR**

Target optimizations:
- Cache test runs: -30%
- Parallel execution: -40%
- Smart test filtering: -20%
- **Target: <60 seconds total**

## Monitoring & Analytics

### Track Workflow Metrics

```bash
# Get workflow runs
gh run list --workflow phase2-release-guardian.yml --limit 20

# Get specific run details
gh run view <run-id> --json status,conclusion,durationMinutes

# Get workflow statistics
gh run list --workflow phase2-release-guardian.yml \
  --json conclusion \
  --jq 'group_by(.conclusion) | map({status: .[0].conclusion, count: length})'
```

### Export Results

```bash
# Download all artifacts from a run
gh run download <run-id> -D ./run_results

# Parse decision from JSON
python -c "
import json
with open('deployment_decision.json') as f:
    d = json.load(f)
    print(f'Decision: {d[\"status\"]}')
    print(f'Confidence: {d[\"confidence\"]}%')
"
```

### Build Dashboard

Create metrics file from workflow results:

```bash
# Script to collect metrics
cat > collect_metrics.sh << 'EOF'
#!/bin/bash
METRICS_FILE="metrics.json"
echo "{" > $METRICS_FILE

# Get last 30 workflow runs
gh run list --workflow phase2-release-guardian.yml \
  --limit 30 \
  --json status,conclusion,createdAt,durationMinutes \
  >> $METRICS_FILE

echo "}" >> $METRICS_FILE
echo "✓ Metrics collected to $METRICS_FILE"
EOF

chmod +x collect_metrics.sh
./collect_metrics.sh
```

## Production Deployment

### Phase 2 → Production

**Requirements before production:**
- ✅ All Phase 2 agents tested and working
- ✅ Workflow successfully triggers and completes
- ✅ Decision logic validated on 10+ PRs
- ✅ Team trained on GO/GATE/NO-GO outcomes
- ✅ Runbooks created for GATE approvals

**Production rollout:**

```bash
# Stage 1: Shadow Mode (no auto-merge)
# - Decisions made but not enforced
# - Monitor decision accuracy
# - Collect feedback for 1 week

# Stage 2: Controlled Rollout
# - Enable auto-merge for low-risk PRs
# - GATE all medium-risk
# - NO-GO blocks high-risk
# - Monitor for 2 weeks

# Stage 3: Full Deployment
# - All decision types fully active
# - Auto-merge enabled
# - Monitor continuously
```

**Switch production:**

```bash
# In workflow YAML, set production mode
env:
  PRODUCTION_MODE: true  # Enable auto-merge
  DECISION_ENFORCEMENT: true  # Enforce decisions
```

## Rollback Plan

If issues occur in production:

```bash
# 1. Disable workflow
git checkout main
git rm .github/workflows/phase2-release-guardian.yml
git commit -m "Rollback: Disable Phase 2 workflow"
git push origin main

# 2. Verify workflow disabled
# Check Actions tab - workflow should not appear

# 3. Investigate issue
# Review recent workflow logs
# Check decision logic and agent outputs

# 4. Fix and redeploy
# Make corrections to agents
# Re-enable workflow
git add .github/workflows/phase2-release-guardian.yml
git commit -m "Fix: Re-enable Phase 2 with fixes"
git push origin main
```

## Next Steps

1. **Test Phase 2:** Run on ai-release-guardian with test PR
2. **Gather Feedback:** Collect team feedback on decisions
3. **Iterate Logic:** Refine thresholds based on outcomes
4. **Expand:** Roll out to other repositories
5. **Measure:** Track QA velocity improvements

## Additional Resources

- [Phase 2 Guide](PHASE2_GUIDE.md) - Detailed Phase 2 documentation
- [Architecture Overview](ARCHITECTURE.md) - System design
- [Agent API Reference](API_REFERENCE.md) - Agent methods
- [GitHub Actions Docs](https://docs.github.com/en/actions)
