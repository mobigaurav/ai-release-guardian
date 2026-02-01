# AI Release Guardian Phase 2 - Deployment & Demonstration Plan

## Overview

This document outlines the complete sequence of steps to:
1. Push the project to GitHub
2. Deploy SAM project to AWS
3. Execute a comprehensive demonstration

**Timeline:** ~2-4 hours total
**Complexity:** Medium (requires AWS & GitHub configuration)

---

## Part 1: Prerequisites & Verification

### Step 1.1: Verify Prerequisites

Before starting, ensure you have:

```bash
# Git
git --version          # v2.30+

# GitHub CLI
gh --version           # v2.0+

# AWS CLI
aws --version          # v2.1+

# SAM CLI
sam --version          # v1.50+

# Python
python --version       # 3.11+

# Docker (for SAM local testing)
docker --version       # 20.10+
```

### Step 1.2: Verify Project Structure

```bash
cd /Users/gauravkumar/Desktop/pproject/myaiprojects/ai-release-guardian

# Check critical files exist
ls -la requirements.txt
ls -la lambda/template.yaml
ls -la .github/workflows/phase2-release-guardian.yml
ls -la src/agents/phase2_orchestrator.py

# All should exist - if any missing, build is incomplete
```

### Step 1.3: Verify All Source Files

```bash
# Check Phase 2 agents
ls src/agents/test_*.py src/agents/deployment_*.py src/agents/phase2_*.py

# Check integrations
ls src/integrations/*.py

# Check documentation
ls docs/PHASE2*.md
```

---

## Part 2: GitHub Setup & Push

### Step 2.1: Create GitHub Repository

**Option A: Via GitHub CLI**

```bash
# Authenticate if not already done
gh auth login

# Create repository
gh repo create ai-release-guardian \
  --public \
  --source=. \
  --remote=origin \
  --push

# Wait for push to complete
# Verify: gh repo view (should show your repo)
```

**Option B: Via GitHub Web UI**

1. Go to https://github.com/new
2. Repository name: `ai-release-guardian`
3. Description: "Automated QA Pipeline with Phase 1 & Phase 2"
4. Make it **Public** (for demonstration)
5. Click "Create repository"

### Step 2.2: Initialize Local Git Repository

```bash
cd /Users/gauravkumar/Desktop/pproject/myaiprojects/ai-release-guardian

# If not already initialized
git init
git add .
git commit -m "Initial commit: Phase 1 & Phase 2 complete"

# Add remote (replace YOUR_GITHUB_USERNAME)
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/ai-release-guardian.git

# Push to main
git branch -M main
git push -u origin main
```

### Step 2.3: Verify GitHub Repository

```bash
# Check repo is live
gh repo view

# Expected output:
# name:    ai-release-guardian
# description: Automated QA Pipeline
# owner: YOUR_GITHUB_USERNAME
# visibility: public
```

**Expected URL:** `https://github.com/YOUR_GITHUB_USERNAME/ai-release-guardian`

---

## Part 3: Configure GitHub Repository Secrets

### Step 3.1: Set Required Secrets

These secrets enable Phase 2 workflow to execute:

```bash
# 1. GITHUB_TOKEN (auto-provided by GitHub Actions)
#    No setup needed - GitHub automatically provides this

# 2. CLAUDE_API_KEY (required for AI analysis)
gh secret set CLAUDE_API_KEY --body "sk-ant-xxxxxxxxxxxxx"

# 3. JIRA_API_TOKEN (optional, for AC extraction)
gh secret set JIRA_API_TOKEN --body "your-jira-api-token"

# 4. JIRA_DOMAIN (optional)
gh secret set JIRA_DOMAIN --body "your-domain.atlassian.net"

# 5. JIRA_PROJECT_KEY (optional)
gh secret set JIRA_PROJECT_KEY --body "ABC"
```

### Step 3.2: Verify Secrets Are Set

```bash
# List all secrets
gh secret list

# Expected output:
# CLAUDE_API_KEY    Updated 2026-02-01
# JIRA_API_TOKEN    Updated 2026-02-01
# etc.
```

### Step 3.3: Get API Keys if Not Available

**Claude API Key:**
1. Go to https://console.anthropic.com/keys
2. Create new API key
3. Copy and save: `sk-ant-xxxxxxxxxxxxx`

**GitHub Token:**
1. Go to https://github.com/settings/tokens
2. Create "Personal access token (classic)"
3. Scopes: repo, workflow, read:org
4. Copy and save

**Jira API Token:**
1. Go to https://id.atlassian.com/manage-profile/security
2. Create API token
3. Copy and save

---

## Part 4: AWS Setup & SAM Deployment

### Step 4.1: Configure AWS Credentials

**Option A: Via AWS CLI**

```bash
# Configure AWS credentials (if not already done)
aws configure

# Prompts:
# AWS Access Key ID: YOUR_ACCESS_KEY
# AWS Secret Access Key: YOUR_SECRET_KEY
# Default region: us-east-1 (or your preferred region)
# Default output format: json
```

**Option B: Via Environment Variables**

```bash
export AWS_ACCESS_KEY_ID="YOUR_ACCESS_KEY"
export AWS_SECRET_ACCESS_KEY="YOUR_SECRET_KEY"
export AWS_DEFAULT_REGION="us-east-1"
```

**Option C: Via AWS SSO**

```bash
aws sso login --profile your-profile
export AWS_PROFILE=your-profile
```

### Step 4.2: Verify AWS Credentials

```bash
# Test credentials
aws sts get-caller-identity

# Expected output:
# {
#     "UserId": "AIDXXXXXXXXXXX",
#     "Account": "123456789012",
#     "Arn": "arn:aws:iam::123456789012:user/your-user"
# }
```

### Step 4.3: Create S3 Bucket for SAM Deployments

```bash
# Create S3 bucket (must be unique globally)
BUCKET_NAME="ai-release-guardian-sam-$(date +%s)"

aws s3 mb s3://$BUCKET_NAME --region us-east-1

echo "S3 Bucket: $BUCKET_NAME"
# Save this for Step 4.5
```

### Step 4.4: Prepare SAM Template

```bash
cd /Users/gauravkumar/Desktop/pproject/myaiprojects/ai-release-guardian

# Verify SAM template exists and is valid
cat lambda/template.yaml

# Expected: CloudFormation template with:
# - Lambda function resource
# - API Gateway resource
# - IAM role for Lambda
# - Environment variables
```

### Step 4.5: Build SAM Project

```bash
cd /Users/gauravkumar/Desktop/pproject/myaiprojects/ai-release-guardian

# Build SAM project
sam build --template lambda/template.yaml

# Expected output:
# Running PythonPipBuilder:python3.11
# Build Succeeded
# Built artifacts are now in .aws-sam/build directory
```

### Step 4.6: Deploy SAM Project to AWS

```bash
# Deploy to AWS (first time - guided)
sam deploy --guided \
  --template-file lambda/template.yaml \
  --s3-bucket $BUCKET_NAME \
  --region us-east-1

# Prompts:
# Stack name: ai-release-guardian
# Region: us-east-1
# Confirm changes before deploy: Y
# Allow SAM CLI to create roles: Y
# Save parameters to samconfig.toml: Y
```

**Alternatively, non-interactive:**

```bash
sam deploy \
  --template-file lambda/template.yaml \
  --s3-bucket $BUCKET_NAME \
  --region us-east-1 \
  --stack-name ai-release-guardian \
  --capabilities CAPABILITY_IAM \
  --no-confirm-changeset
```

### Step 4.7: Verify Lambda Deployment

```bash
# List Lambda functions
aws lambda list-functions --region us-east-1 | grep ai-release-guardian

# Expected: You should see the ai-release-guardian function listed

# Get function details
aws lambda get-function \
  --function-name ai-release-guardian \
  --region us-east-1

# Expected output includes:
# - Function ARN
# - Role ARN
# - Handler: lambda.handler
# - Runtime: python3.11
# - Environment variables
```

### Step 4.8: Get API Gateway Endpoint

```bash
# Get CloudFormation stack outputs
aws cloudformation describe-stacks \
  --stack-name ai-release-guardian \
  --region us-east-1 \
  --query 'Stacks[0].Outputs'

# Expected output:
# [
#     {
#         "OutputKey": "ReleaseGuardianApi",
#         "OutputValue": "https://xxxxx.execute-api.us-east-1.amazonaws.com/Prod"
#     }
# ]

# Save this URL for testing
API_ENDPOINT="https://xxxxx.execute-api.us-east-1.amazonaws.com/Prod"
```

### Step 4.9: Configure Lambda Environment Variables

```bash
# Update Lambda environment variables
aws lambda update-function-configuration \
  --function-name ai-release-guardian \
  --environment Variables="{
    GITHUB_TOKEN=ghp_xxxxxxxxxxxxx,
    CLAUDE_API_KEY=sk-ant-xxxxxxxxxxxxx,
    JIRA_API_TOKEN=your-token,
    JIRA_DOMAIN=your-domain.atlassian.net
  }" \
  --region us-east-1

# Verify
aws lambda get-function-configuration \
  --function-name ai-release-guardian \
  --region us-east-1 \
  --query 'Environment'
```

---

## Part 5: GitHub Webhook Configuration (Optional)

### Step 5.1: Create GitHub Webhook

```bash
# Add webhook to repository
gh repo webhook add \
  --events pull_request,push \
  --payload-url $API_ENDPOINT/analyze-release \
  --active

# Or via GitHub UI:
# Settings → Webhooks → Add webhook
# Payload URL: $API_ENDPOINT/analyze-release
# Content type: application/json
# Events: Pull requests, Pushes
# Active: Yes
```

### Step 5.2: Verify Webhook

```bash
# List webhooks
gh repo webhook list

# Expected: Your webhook URL should appear
```

---

## Part 6: Local Testing

### Step 6.1: Test Phase 2 Orchestrator Locally

```bash
cd /Users/gauravkumar/Desktop/pproject/myaiprojects/ai-release-guardian

# Install dependencies
pip install -r requirements.txt

# Test orchestrator initialization
python -c "from src.agents import create_phase2_orchestrator; print('✓ Orchestrator loaded')"

# Test end-to-end command (help)
python -m src.agents.phase2_orchestrator end-to-end --help
```

### Step 6.2: Run Local Demo

```bash
# Run complete pipeline locally
python -m src.agents.phase2_orchestrator end-to-end \
  --repo-owner "YOUR_GITHUB_USERNAME" \
  --repo-name "ai-release-guardian" \
  --pr-number 1 \
  --repo-path . \
  --output-dir ./demo_results

# Check results
cat demo_results/deployment_decision.json | python -m json.tool
```

---

## Part 7: Demonstration - Create Test PR

### Step 7.1: Create Test Branch

```bash
cd /Users/gauravkumar/Desktop/pproject/myaiprojects/ai-release-guardian

# Create feature branch
git checkout -b demo/phase2-demonstration

# Add demonstration test file
cat > tests/test_phase2_demo.py << 'EOF'
"""
Phase 2 Demonstration Tests
Tests to demonstrate Phase 2 agents in action
"""
import pytest

class TestPhase2Demonstration:
    """Tests to demonstrate Phase 2 capabilities"""
    
    def test_demo_feature_one_success(self):
        """
        AC-1: User can login successfully
        Test: Verify login with valid credentials
        """
        assert True, "Feature one works correctly"
    
    def test_demo_feature_two_success(self):
        """
        AC-2: User dashboard loads correctly
        Test: Verify dashboard renders
        """
        assert True, "Feature two works correctly"
    
    def test_demo_feature_three_success(self):
        """
        AC-3: Export functionality works
        Test: Verify data export
        """
        assert True, "Feature three works correctly"
    
    @pytest.mark.skip(reason="This test intentionally skipped for demo")
    def test_demo_untested_ac(self):
        """
        AC-4: Advanced settings page (UNTESTED)
        This AC is not covered by tests - Phase 2 will flag coverage gap
        """
        pass

# Additional tests for coverage
class TestPhase2Coverage:
    """Additional tests to show coverage metrics"""
    
    def test_integration_feature_one(self):
        """Integration test for feature one"""
        assert 1 + 1 == 2
    
    def test_integration_feature_two(self):
        """Integration test for feature two"""
        assert True
    
    def test_unit_helper_function(self):
        """Unit test for helper"""
        assert True
EOF

# Commit changes
git add tests/test_phase2_demo.py
git commit -m "Demo: Add Phase 2 demonstration tests"

# Push to GitHub
git push origin demo/phase2-demonstration
```

### Step 7.2: Create Pull Request

**Option A: Via GitHub CLI**

```bash
# Create PR
gh pr create \
  --title "Demo: Phase 2 Automated QA Pipeline" \
  --body "# Phase 2 Demonstration

This PR demonstrates the complete Phase 2 automated QA pipeline:

## What Will Happen
1. **Phase 1**: Tests will be generated and risk scored
2. **Phase 2**: Generated tests will be executed
3. **Phase 2**: Test results will be validated against AC
4. **Phase 2**: Deployment decision will be made (GO/GATE/NO-GO)

## Expected Outcome
- ✅ Tests generated and executed
- ✅ AC coverage validated
- ✅ GO decision (all tests pass, coverage good, low risk)
- ✅ PR auto-merged

Watch the Actions tab for real-time progress!" \
  --base main \
  --head demo/phase2-demonstration
```

**Option B: Via GitHub Web UI**

1. Go to your repository
2. Click "Compare & pull request"
3. Set:
   - Title: "Demo: Phase 2 Automated QA Pipeline"
   - Description: (as shown above)
4. Click "Create pull request"

### Step 7.3: Monitor GitHub Actions

```bash
# Watch workflow in real-time
gh run watch

# Or get status
gh run list --workflow phase2-release-guardian.yml --limit 5

# Get detailed output
gh run view <run-id> --log
```

---

## Part 8: Demonstration Scenarios

### Scenario 1: GO Decision (Happy Path)

**Setup:** Already created with Step 7.1

**Expected Flow:**
1. Phase 1: Tests generated (3-5 test scenarios)
2. Phase 2: Tests execute (all pass)
3. Phase 2: AC coverage validated (≥80%)
4. Phase 2: GO decision (confidence 85-95%)
5. Action: Auto-merge + deploy to staging

**Verification:**
```bash
# Check PR comment
gh pr view <pr-number> --comments

# Check if merged
gh pr view <pr-number> --json state
```

---

### Scenario 2: GATE Decision (Manual Approval Path)

**Setup:** Create PR with risky changes

```bash
git checkout -b demo/phase2-risky-changes

# Simulate risky change: database migration
cat > src/db_migration_risky.py << 'EOF'
"""
Risky database migration - triggers GATE decision
"""
# This file triggers high risk pattern detection
# Phase 2 will require manual review before deployment
EOF

git add src/db_migration_risky.py
git commit -m "Demo: Database schema migration (risky - should trigger GATE)"
git push origin demo/phase2-risky-changes

# Create PR
gh pr create \
  --title "Demo: Risky Change (GATE Decision)" \
  --body "This PR contains database schema changes.

Expected outcome: GATE decision (requires DBA approval)" \
  --base main \
  --head demo/phase2-risky-changes
```

**Expected Outcome:**
1. Phase 1: Tests generated
2. Phase 2: Tests execute
3. Phase 2: AC coverage validated
4. Phase 2: GATE decision (risk ≥50 + DB changes)
5. Action: Post gates, wait for approval

**Verification:**
```bash
# Check PR comment for gates
gh pr view <pr-number> --comments | grep "DBA_REVIEW"

# Manually approve by commenting
gh pr comment <pr-number> -b "Approved by DBA"
```

---

### Scenario 3: NO-GO Decision (Failure Path)

**Setup:** Create PR with failing tests

```bash
git checkout -b demo/phase2-failing-tests

# Add test that will fail
cat > tests/test_phase2_fail.py << 'EOF'
def test_intentional_failure():
    """This test intentionally fails to demonstrate NO-GO"""
    assert False, "This test fails to trigger NO-GO decision"
EOF

git add tests/test_phase2_fail.py
git commit -m "Demo: Add failing test (should trigger NO-GO)"
git push origin demo/phase2-failing-tests

# Create PR
gh pr create \
  --title "Demo: Failing Test (NO-GO Decision)" \
  --body "This PR contains a failing test.

Expected outcome: NO-GO decision (tests fail)" \
  --base main \
  --head demo/phase2-failing-tests
```

**Expected Outcome:**
1. Phase 1: Tests generated
2. Phase 2: Tests execute (FAIL)
3. Phase 2: NO-GO decision
4. Action: Post failures, block merge

**Verification:**
```bash
# Check PR comment for failures
gh pr view <pr-number> --comments | grep "FAILED\|NO-GO"

# Fix test and retry
# PR should show new workflow execution
```

---

## Part 9: Monitoring & Metrics

### Step 9.1: Collect Workflow Metrics

```bash
# Get all workflow runs
gh run list \
  --workflow phase2-release-guardian.yml \
  --json status,conclusion,createdAt,durationMinutes \
  --limit 20

# Example analysis script
cat > collect_metrics.py << 'EOF'
import json
import subprocess
from datetime import datetime

# Get latest 10 runs
result = subprocess.run([
    'gh', 'run', 'list',
    '--workflow', 'phase2-release-guardian.yml',
    '--json', 'status,conclusion,createdAt,durationMinutes',
    '--limit', '10'
], capture_output=True, text=True)

runs = json.loads(result.stdout)

print("\n=== Workflow Execution Metrics ===\n")
print(f"Total runs: {len(runs)}")

successes = sum(1 for r in runs if r['conclusion'] == 'success')
failures = sum(1 for r in runs if r['conclusion'] == 'failure')

print(f"Successful: {successes}")
print(f"Failed: {failures}")

if runs:
    avg_duration = sum(r['durationMinutes'] for r in runs) / len(runs)
    print(f"Average duration: {avg_duration:.1f} minutes")

print("\nDetailed Results:")
for i, run in enumerate(runs, 1):
    print(f"{i}. {run['conclusion'].upper()} - {run['durationMinutes']}min - {run['createdAt']}")
EOF

python collect_metrics.py
```

### Step 9.2: Track Decision Distribution

```bash
# Script to analyze decision distribution
cat > analyze_decisions.py << 'EOF'
import json
import subprocess

# Get artifacts from all runs
result = subprocess.run([
    'gh', 'run', 'list',
    '--workflow', 'phase2-release-guardian.yml',
    '--json', 'databaseId',
    '--limit', '20'
], capture_output=True, text=True)

runs = json.loads(result.stdout)

decisions = {'GO': 0, 'GATE': 0, 'NO-GO': 0}

for run in runs:
    # Download and parse deployment_decision.json
    # (This requires more complex artifact handling)
    pass

print("\n=== Decision Distribution ===")
print(f"GO decisions:    {decisions['GO']}")
print(f"GATE decisions:  {decisions['GATE']}")
print(f"NO-GO decisions: {decisions['NO-GO']}")

if sum(decisions.values()) > 0:
    go_rate = decisions['GO'] / sum(decisions.values()) * 100
    print(f"\nAuto-merge rate: {go_rate:.1f}%")
EOF

python analyze_decisions.py
```

### Step 9.3: Measure QA Velocity

```bash
# Time from PR creation to merge
cat > measure_velocity.sh << 'EOF'
#!/bin/bash

echo "=== QA Velocity Metrics ==="
echo ""

# Get recent merged PRs
gh pr list \
  --state merged \
  --limit 10 \
  --json number,title,createdAt,mergedAt \
  --jq '.[] | {pr: .number, title: .title, created: .createdAt, merged: .mergedAt}'

# Parse and calculate average time-to-merge
echo ""
echo "Average time from PR creation to merge:"
gh pr list --state merged --limit 20 --json number,createdAt,mergedAt \
  --jq '[.[] | {
    created: (.createdAt | fromdateiso8601),
    merged: (.mergedAt | fromdateiso8601)
  } | .merged - .created | . / 60] | add / length | . / 60 | round' | xargs -I {} echo "{} hours"
EOF

chmod +x measure_velocity.sh
./measure_velocity.sh
```

---

## Part 10: Complete Orchestration Summary

### Timeline & Sequence

| Step | Task | Time | Status |
|------|------|------|--------|
| 1 | Verify prerequisites | 5 min | ⚪ |
| 2 | GitHub repo setup | 5 min | ⚪ |
| 3 | Configure secrets | 5 min | ⚪ |
| 4 | AWS setup | 10 min | ⚪ |
| 5 | SAM build & deploy | 20 min | ⚪ |
| 6 | Local testing | 10 min | ⚪ |
| 7 | Create test PRs | 15 min | ⚪ |
| 8 | Monitor workflows | 30 min | ⚪ |
| 9 | Collect metrics | 15 min | ⚪ |
| 10 | Documentation | 10 min | ⚪ |
| **Total** | **Complete Deployment** | **~2.5 hours** | |

### Verification Checklist

- [ ] Git repo initialized and pushed to GitHub
- [ ] GitHub Actions workflows appearing in Actions tab
- [ ] Repository secrets configured (CLAUDE_API_KEY, etc.)
- [ ] AWS credentials verified
- [ ] SAM project built successfully
- [ ] Lambda function deployed to AWS
- [ ] API Gateway endpoint accessible
- [ ] GitHub webhook configured (optional)
- [ ] Phase 2 orchestrator works locally
- [ ] Test PR created successfully
- [ ] GitHub Actions workflow triggered on PR
- [ ] Phase 1 job completed (tests generated)
- [ ] Phase 2 executor job completed (tests ran)
- [ ] Phase 2 validator job completed (AC coverage checked)
- [ ] Phase 2 decider job completed (decision made)
- [ ] PR comment posted with decision
- [ ] GO/GATE/NO-GO decision logic verified
- [ ] Metrics collected and analyzed

### Success Criteria

✅ **All Phase 2 Components Working:**
- Tests execute successfully
- AC coverage validated
- Decisions made with confidence scores
- PR comments posted correctly

✅ **Workflow Automation:**
- Auto-merge works for GO decisions
- Merge blocks for NO-GO decisions
- Gates posted for GATE decisions

✅ **Performance:**
- Workflow completes in <3 minutes
- All jobs execute sequentially
- No timeout errors

✅ **Monitoring:**
- Metrics collected successfully
- Decision distribution tracked
- QA velocity measured

---

## Troubleshooting Guide

### GitHub Issues

**Workflow not triggering:**
```bash
# Check workflow syntax
yamllint .github/workflows/phase2-release-guardian.yml

# Check workflow is committed
git log --oneline -- .github/workflows/

# Re-trigger manually
gh workflow run phase2-release-guardian.yml
```

**Missing secrets:**
```bash
# Verify all required secrets set
gh secret list

# Add missing secret
gh secret set SECRET_NAME --body "value"
```

### AWS Issues

**Lambda deployment fails:**
```bash
# Check SAM template syntax
sam validate

# Rebuild
sam build --template lambda/template.yaml

# Check CloudFormation events
aws cloudformation describe-stack-events \
  --stack-name ai-release-guardian \
  --region us-east-1 | head -20
```

**Lambda timeout:**
```bash
# Increase timeout in template.yaml
# Change: Timeout: 30 → Timeout: 120

sam deploy
```

### Workflow Execution Issues

**Tests not running:**
```bash
# Check pytest installed
python -m pytest --version

# Run tests manually
pytest tests/ -v

# Check test file location
find . -name "test_*.py" -type f
```

---

## Next Steps After Demonstration

1. **Document Learnings**
   - Record decision accuracy
   - Note any threshold adjustments needed
   - Collect team feedback

2. **Iterate & Improve**
   - Refine decision logic based on outcomes
   - Optimize workflow performance
   - Add additional test scenarios

3. **Expand to Production**
   - Deploy to additional repositories
   - Monitor across all repos
   - Scale CI/CD infrastructure

4. **Plan Phase 3**
   - Performance testing automation
   - Security test automation
   - Advanced analytics dashboard

---

## Key Contacts & Resources

**GitHub:**
- Repository: `https://github.com/YOUR_USERNAME/ai-release-guardian`
- Actions: `https://github.com/YOUR_USERNAME/ai-release-guardian/actions`
- Settings: `https://github.com/YOUR_USERNAME/ai-release-guardian/settings`

**AWS:**
- Lambda Console: `https://console.aws.amazon.com/lambda`
- CloudFormation: `https://console.aws.amazon.com/cloudformation`
- API Gateway: `https://console.aws.amazon.com/apigateway`

**Documentation:**
- Phase 2 Guide: `docs/PHASE2_GUIDE.md`
- Deployment Guide: `docs/PHASE2_DEPLOYMENT.md`
- Quick Reference: `docs/PHASE2_QUICK_REFERENCE.md`

---

**Status:** Ready for Deployment & Demonstration
**Version:** 2.0 - Complete Phase 1 + Phase 2
**Date:** February 1, 2026
