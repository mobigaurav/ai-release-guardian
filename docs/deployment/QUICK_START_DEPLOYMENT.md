# Deployment & Demonstration - Quick Start Guide

## 📋 Complete Step-by-Step Sequence

### Phase A: Prerequisites (10 minutes)

```bash
# 1. Verify all required tools
git --version
gh --version
aws --version
sam --version
python --version
docker --version

# 2. Navigate to project
cd /Users/gauravkumar/Desktop/pproject/myaiprojects/ai-release-guardian

# 3. Verify project structure
ls -la requirements.txt lambda/template.yaml .github/workflows/
ls src/agents/test_*.py src/agents/deployment_*.py src/agents/phase2_*.py
```

**✓ What to verify:** All tools show version numbers, all files exist

---

### Phase B: GitHub Setup (15 minutes)

#### Step 1: Create GitHub Repository

```bash
# Option A: Via CLI
gh auth login  # If needed
gh repo create ai-release-guardian --public --source=. --remote=origin --push

# Option B: Via Web UI at https://github.com/new
# - Name: ai-release-guardian
# - Description: Automated QA Pipeline with Phase 1 & Phase 2
# - Public
# - Create repository
```

#### Step 2: Initialize & Push Local Repository

```bash
cd /Users/gauravkumar/Desktop/pproject/myaiprojects/ai-release-guardian

# If already created via CLI, skip to git push
git init
git add .
git commit -m "Initial commit: Phase 1 & Phase 2 complete"
git remote add origin https://github.com/YOUR_USERNAME/ai-release-guardian.git
git branch -M main
git push -u origin main
```

#### Step 3: Configure Repository Secrets

```bash
# CLAUDE_API_KEY (Required)
gh secret set CLAUDE_API_KEY --body "sk-ant-xxxxxxxxxxxxx"

# JIRA_API_TOKEN (Optional - for AC extraction)
gh secret set JIRA_API_TOKEN --body "your-jira-api-token"

# JIRA_DOMAIN (Optional)
gh secret set JIRA_DOMAIN --body "your-domain.atlassian.net"

# JIRA_PROJECT_KEY (Optional)
gh secret set JIRA_PROJECT_KEY --body "ABC"

# Verify
gh secret list
```

**✓ What to expect:** 
- Repository shows at `https://github.com/YOUR_USERNAME/ai-release-guardian`
- Workflow visible in Actions tab
- Secrets listed (marked with Last Updated timestamp)

---

### Phase C: AWS Setup & SAM Deployment (30 minutes)

#### Step 1: Configure AWS Credentials

```bash
# Option A: Interactive setup
aws configure
# Enter: Access Key, Secret Key, Region (us-east-1), Output format (json)

# Option B: Environment variables
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="us-east-1"

# Verify credentials
aws sts get-caller-identity
```

#### Step 2: Create S3 Bucket

```bash
# Create unique bucket name
BUCKET_NAME="ai-release-guardian-sam-$(date +%s)"

# Create bucket
aws s3 mb s3://$BUCKET_NAME --region us-east-1

# Save for later
echo "Bucket: $BUCKET_NAME" > aws_config.txt
```

#### Step 3: Build & Deploy SAM Project

```bash
cd /Users/gauravkumar/Desktop/pproject/myaiprojects/ai-release-guardian

# Build
sam build --template lambda/template.yaml

# Deploy (first time - guided)
sam deploy --guided \
  --template-file lambda/template.yaml \
  --s3-bucket $BUCKET_NAME \
  --region us-east-1

# Or non-interactive
sam deploy \
  --template-file lambda/template.yaml \
  --s3-bucket $BUCKET_NAME \
  --region us-east-1 \
  --stack-name ai-release-guardian \
  --capabilities CAPABILITY_IAM \
  --no-confirm-changeset
```

#### Step 4: Verify Deployment

```bash
# Get API endpoint
API_ENDPOINT=$(aws cloudformation describe-stacks \
  --stack-name ai-release-guardian \
  --region us-east-1 \
  --query 'Stacks[0].Outputs[0].OutputValue' \
  --output text)

echo "API Endpoint: $API_ENDPOINT"

# Get Lambda function
aws lambda get-function \
  --function-name ai-release-guardian \
  --region us-east-1 \
  --query 'Configuration.FunctionArn' \
  --output text
```

#### Step 5: Configure Lambda Environment Variables

```bash
aws lambda update-function-configuration \
  --function-name ai-release-guardian \
  --environment Variables="{
    GITHUB_TOKEN=ghp_xxxxxxxxxxxxx,
    CLAUDE_API_KEY=sk-ant-xxxxxxxxxxxxx,
    JIRA_API_TOKEN=your-token,
    JIRA_DOMAIN=your-domain.atlassian.net
  }" \
  --region us-east-1
```

**✓ What to expect:**
- SAM build completes successfully
- Lambda function appears in AWS console
- API Gateway endpoint accessible
- Environment variables set correctly

---

### Phase D: Local Testing (15 minutes)

#### Step 1: Install Dependencies

```bash
cd /Users/gauravkumar/Desktop/pproject/myaiprojects/ai-release-guardian

# Install all required packages
pip install -r requirements.txt

# Verify Phase 2 orchestrator loads
python -c "from src.agents import create_phase2_orchestrator; print('✓ Ready')"
```

#### Step 2: Run Local Demo

```bash
# Generate, execute, validate, and decide
python -m src.agents.phase2_orchestrator end-to-end \
  --repo-owner "YOUR_GITHUB_USERNAME" \
  --repo-name "ai-release-guardian" \
  --pr-number 1 \
  --repo-path . \
  --output-dir ./demo_results

# Check the decision
cat demo_results/deployment_decision.json | python -m json.tool

# Expected output: GO/GATE/NO-GO with confidence score and reasoning
```

**✓ What to expect:**
- 4 JSON files created: tests_generated, tests_executed, tests_validated, deployment_decision
- Decision status: GO, GATE, or NO-GO
- Confidence score: 0-100%
- Reasoning and next steps provided

---

### Phase E: Create Test PR (15 minutes)

#### Step 1: Create Feature Branch with Demo Tests

```bash
cd /Users/gauravkumar/Desktop/pproject/myaiprojects/ai-release-guardian

# Create branch
git checkout -b demo/phase2-test

# Create demo test file
cat > tests/test_demo.py << 'EOF'
"""Phase 2 Demo Tests"""
import pytest

def test_feature_one():
    """AC-1: Feature one"""
    assert True

def test_feature_two():
    """AC-2: Feature two"""
    assert True

def test_feature_three():
    """AC-3: Feature three"""
    assert True

@pytest.mark.skip(reason="Demo: Shows coverage gap")
def test_untested_ac():
    """AC-4: Not tested - coverage gap"""
    pass
EOF

# Commit and push
git add tests/test_demo.py
git commit -m "Demo: Add Phase 2 test scenarios"
git push origin demo/phase2-test
```

#### Step 2: Create Pull Request

```bash
# Via CLI
gh pr create \
  --title "Demo: Phase 2 Automated QA" \
  --body "# Phase 2 Demonstration

This PR demonstrates:
- Phase 1: Test generation + risk scoring
- Phase 2: Test execution + validation
- Phase 2: Deployment decision (GO/GATE/NO-GO)

Watch Actions tab for real-time progress!" \
  --base main \
  --head demo/phase2-test

# Note the PR number from output
# Via Web UI: Click "Compare & pull request" button
```

#### Step 3: Monitor Workflow

```bash
# Watch in real-time
gh run watch

# Or check status
gh run list --workflow phase2-release-guardian.yml --limit 5

# Get detailed logs
gh run view <run-id> --log

# Check PR comment
gh pr view <pr-number> --comments
```

**✓ What to expect:**
- GitHub Actions workflow triggers automatically
- 5 jobs execute sequentially (within 2-3 minutes)
- PR comment appears with decision and reasoning
- If GO: PR auto-merges

---

### Phase F: Test All Decision Paths (30 minutes)

#### Scenario 1: GO Decision (Happy Path)
Already tested in Phase E! ✅

#### Scenario 2: GATE Decision (Risky Changes)

```bash
git checkout -b demo/gate-test

# Add risky change (database migration)
cat > src/db_migration.py << 'EOF'
"""
Database schema migration
Triggers GATE decision due to high risk
"""
EOF

git add src/db_migration.py
git commit -m "Demo: DB migration (triggers GATE)"
git push origin demo/gate-test

# Create PR
gh pr create \
  --title "Demo: GATE Decision" \
  --body "Database schema changes - expect GATE decision"

# Monitor workflow → Check for GATE decision + DBA approval gate
```

#### Scenario 3: NO-GO Decision (Failing Tests)

```bash
git checkout -b demo/no-go-test

# Add failing test
cat > tests/test_fail.py << 'EOF'
def test_intentional_failure():
    """Intentionally failing test"""
    assert False, "Demo: This test fails"
EOF

git add tests/test_fail.py
git commit -m "Demo: Add failing test (triggers NO-GO)"
git push origin demo/no-go-test

# Create PR
gh pr create \
  --title "Demo: NO-GO Decision" \
  --body "Intentionally failing test - expect NO-GO decision"

# Monitor workflow → Check for NO-GO decision + merge block
```

**✓ What to verify:**
- GO: Auto-merge works, PR merged
- GATE: Gates posted in comment, waiting for approval
- NO-GO: Merge blocked, failures listed

---

### Phase G: Collect Metrics (15 minutes)

#### Step 1: Workflow Metrics

```bash
# Get all workflow runs
gh run list \
  --workflow phase2-release-guardian.yml \
  --json status,conclusion,createdAt,durationMinutes \
  --limit 10

# Expected: Shows all runs with their status and duration
```

#### Step 2: Decision Distribution

```bash
# Create analysis script
cat > analyze_phase2.py << 'EOF'
import subprocess
import json

result = subprocess.run([
    'gh', 'run', 'list',
    '--workflow', 'phase2-release-guardian.yml',
    '--json', 'conclusion,durationMinutes',
    '--limit', '10'
], capture_output=True, text=True)

runs = json.loads(result.stdout)

print("\n=== Phase 2 Execution Metrics ===")
print(f"Total runs: {len(runs)}")

success = sum(1 for r in runs if r['conclusion'] == 'success')
failed = sum(1 for r in runs if r['conclusion'] == 'failure')
avg_time = sum(r['durationMinutes'] for r in runs) / len(runs) if runs else 0

print(f"Successful: {success}")
print(f"Failed: {failed}")
print(f"Average time: {avg_time:.1f} minutes")
EOF

python analyze_phase2.py
```

**✓ What to capture:**
- Number of workflows executed
- Success rate
- Average execution time
- Decision distribution (GO/GATE/NO-GO counts)
- Time savings vs manual QA

---

## 🎯 Quick Reference Checklist

```
PART A: Prerequisites       [ ] 10 min
PART B: GitHub Setup        [ ] 15 min
PART C: AWS SAM Deploy      [ ] 30 min
PART D: Local Testing       [ ] 15 min
PART E: Create Test PR      [ ] 15 min
PART F: Test Scenarios      [ ] 30 min
PART G: Collect Metrics     [ ] 15 min
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TOTAL TIME                  ≈ 2.5 hours
```

---

## 🚀 Commands Quick Reference

```bash
# GitHub
gh auth login
gh repo create ai-release-guardian --public --source=. --remote=origin --push
gh secret set CLAUDE_API_KEY --body "sk-ant-xxxxxxxxxxxxx"
gh pr create --title "Demo" --body "Description"
gh run list --workflow phase2-release-guardian.yml

# AWS
aws configure
aws sts get-caller-identity
aws s3 mb s3://bucket-name
aws lambda list-functions

# SAM
sam build --template lambda/template.yaml
sam deploy --guided --template-file lambda/template.yaml
sam deploy  # If using samconfig.toml

# Local Testing
python -m src.agents.phase2_orchestrator end-to-end --help
pip install -r requirements.txt
pytest tests/ -v

# Git
git checkout -b feature/branch-name
git add .
git commit -m "message"
git push origin branch-name
```

---

## 📞 Troubleshooting

### GitHub Issues
- Workflow not triggering? → Check secrets are set, workflow file valid
- PR comment missing? → Check Actions tab for job completion

### AWS Issues
- Lambda timeout? → Increase timeout in template.yaml (30 → 120)
- Credentials error? → Run `aws sts get-caller-identity` to verify
- API not accessible? → Check Lambda execution role has proper permissions

### Workflow Issues
- Tests not running? → Verify pytest installed, test files exist
- Validation failing? → Check AC mapping in test names

---

## ✨ Success Criteria

All of these should be true:
- ✅ GitHub repo created and code pushed
- ✅ GitHub Actions workflow visible in Actions tab
- ✅ AWS Lambda function deployed
- ✅ Test PR created and workflow triggered
- ✅ Phase 2 agents executed (all 4 jobs completed)
- ✅ PR comment posted with decision
- ✅ GO/GATE/NO-GO decisions demonstrated
- ✅ Metrics collected and analyzed

---

## 📚 Detailed Guides

For more information, see:
- Full deployment guide: `DEPLOYMENT_AND_DEMO_PLAN.md`
- Phase 2 architecture: `docs/PHASE2_GUIDE.md`
- Commands reference: `docs/PHASE2_QUICK_REFERENCE.md`

---

**Ready to deploy?** Start with Phase A: Prerequisites! 🚀
