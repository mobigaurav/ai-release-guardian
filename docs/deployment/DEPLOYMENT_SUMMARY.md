# 📋 DEPLOYMENT PLAN SUMMARY & EXECUTION GUIDE

## 🎯 Your Complete Roadmap

You've successfully built Phase 1 and Phase 2 of AI Release Guardian. Now it's time to deploy and demonstrate it.

---

## 📊 What You're Deploying

### Phase 1: Test Generation & Risk Scoring ✅ (Already Built)
- **Planner Agent**: Analyzes PR changes and Jira AC
- **Test Generator**: Creates test scenarios via Claude AI
- **Risk Scorer**: Assesses deployment risk
- **Rollback Planner**: Plans rollback procedures

### Phase 2: Test Execution & Deployment Decision ✅ (Already Built)
- **Test Executor**: Runs pytest tests
- **Test Validator**: Validates AC coverage
- **Deployment Decider**: Makes GO/GATE/NO-GO decisions
- **Phase 2 Orchestrator**: Coordinates everything

### Infrastructure
- **GitHub Actions Workflow**: Automated CI/CD pipeline
- **AWS Lambda**: Optional webhook handler
- **API Gateway**: REST API for webhook integration
- **SAM Template**: Infrastructure-as-code

---

## 🚀 Three-Phase Deployment Plan

### **PHASE A: GITHUB SETUP** (15 minutes)

| # | Step | Command | Expected Result |
|---|------|---------|-----------------|
| 1 | Create GitHub repo | `gh repo create ai-release-guardian --public` | Repo created |
| 2 | Push code | `git push -u origin main` | Code on GitHub |
| 3 | Set secrets | `gh secret set CLAUDE_API_KEY --body "..."` | Secrets configured |
| ✓ | **GITHUB READY** | Verify: `gh secret list` | Can see secrets |

**Files involved:**
- `.github/workflows/phase2-release-guardian.yml` - Workflow definition
- Repository secrets - API keys and tokens

**Why this matters:**
- GitHub Actions workflow triggers automatically on PRs
- Secrets enable Phase 2 agents to call Claude, Jira, GitHub APIs
- Repository is your central integration point

---

### **PHASE B: AWS DEPLOYMENT** (30 minutes)

| # | Step | Command | Expected Result |
|---|------|---------|-----------------|
| 1 | Configure AWS | `aws configure` | Credentials set |
| 2 | Create S3 bucket | `aws s3 mb s3://bucket-name` | Bucket for SAM |
| 3 | Build SAM | `sam build --template lambda/template.yaml` | Build succeeds |
| 4 | Deploy SAM | `sam deploy --guided` | Lambda deployed |
| 5 | Get endpoint | `aws cloudformation describe-stacks ...` | Endpoint URL |
| ✓ | **AWS READY** | Test: `curl $API_ENDPOINT` | API responds |

**Files involved:**
- `lambda/template.yaml` - CloudFormation infrastructure
- `lambda/handler.py` - Lambda handler code
- `requirements.txt` - Python dependencies

**Why this matters:**
- Lambda provides optional webhook integration
- API Gateway exposes REST endpoint for GitHub webhooks
- Infrastructure-as-code approach is production-ready

---

### **PHASE C: DEMONSTRATION** (45 minutes)

| # | Step | Command | Expected Result |
|---|------|---------|-----------------|
| 1 | Local test | `python -m src.agents.phase2_orchestrator end-to-end ...` | 4 JSON files created |
| 2 | Create PR | `git checkout -b demo/test && git push && gh pr create` | PR on GitHub |
| 3 | Monitor | `gh run list --workflow phase2-release-guardian.yml` | Jobs executing |
| 4 | Verify GO | Check PR comment | Decision: GO ✅ |
| 5 | Test GATE | Create risky change PR | Decision: GATE ⚠️ |
| 6 | Test NO-GO | Create failing test PR | Decision: NO-GO ❌ |
| ✓ | **DEMO COMPLETE** | All paths demonstrated | All scenarios working |

**Expected workflow:**
- PR created → Workflow triggers → 5 jobs execute → Decision posted

---

## 📝 Step-by-Step Execution

### PHASE A: GitHub Setup (Detailed Steps)

**Step A1: Authenticate with GitHub**
```bash
gh auth login
# Follow prompts to authenticate
# Or if already authenticated, skip this
```

**Step A2: Create Repository**
```bash
# Option 1: Push existing code
gh repo create ai-release-guardian --public --source=. --remote=origin --push

# Option 2: Create on web and push locally
# Go to https://github.com/new, create, then:
cd /path/to/project
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/ai-release-guardian.git
git push -u origin main
```

**Step A3: Configure Secrets**
```bash
# Get API keys first (see section below)

# Set secrets
gh secret set CLAUDE_API_KEY --body "sk-ant-xxxxxxxxxxxxx"
gh secret set JIRA_API_TOKEN --body "your-token"
gh secret set JIRA_DOMAIN --body "your-domain.atlassian.net"

# Verify
gh secret list
```

**✓ Verification: Check GitHub**
- Go to your repo: https://github.com/YOUR_USERNAME/ai-release-guardian
- Check Actions tab - workflow should be visible
- Check Settings → Secrets - all secrets should be listed

---

### PHASE B: AWS Deployment (Detailed Steps)

**Step B1: Configure AWS Credentials**
```bash
aws configure
# Enter: Access Key ID, Secret Access Key, Region, Output format

# Verify
aws sts get-caller-identity
# Should show your AWS account info
```

**Step B2: Create S3 Bucket**
```bash
BUCKET_NAME="ai-release-guardian-$(date +%s)"
aws s3 mb s3://$BUCKET_NAME --region us-east-1

# Save for next steps
echo "export S3_BUCKET=$BUCKET_NAME" >> ~/.bashrc
source ~/.bashrc
```

**Step B3: Build SAM Project**
```bash
cd /path/to/ai-release-guardian
sam build --template lambda/template.yaml

# Should complete with: "Build Succeeded"
```

**Step B4: Deploy SAM**
```bash
sam deploy --guided \
  --template-file lambda/template.yaml \
  --s3-bucket $S3_BUCKET \
  --region us-east-1

# Prompts:
# Stack name: ai-release-guardian
# Region: us-east-1
# Confirm changes before deploy: Y
# Allow SAM CLI IAM role creation: Y
# Save parameters to samconfig.toml: Y
```

**Step B5: Get API Endpoint**
```bash
API_ENDPOINT=$(aws cloudformation describe-stacks \
  --stack-name ai-release-guardian \
  --region us-east-1 \
  --query 'Stacks[0].Outputs[0].OutputValue' \
  --output text)

echo "API Endpoint: $API_ENDPOINT"
# Save this URL!
```

**Step B6: Configure Lambda Environment**
```bash
aws lambda update-function-configuration \
  --function-name ai-release-guardian \
  --environment Variables="{
    GITHUB_TOKEN=ghp_xxxxxxxxxxxxx,
    CLAUDE_API_KEY=sk-ant-xxxxxxxxxxxxx,
    JIRA_API_TOKEN=your-token
  }"
```

**✓ Verification: Check AWS**
- AWS Lambda console: See `ai-release-guardian` function
- AWS CloudFormation: See `ai-release-guardian` stack
- AWS API Gateway: See created API

---

### PHASE C: Demonstration (Detailed Steps)

**Step C1: Local Test**
```bash
cd /path/to/ai-release-guardian

# Install dependencies
pip install -r requirements.txt

# Run complete pipeline
python -m src.agents.phase2_orchestrator end-to-end \
  --repo-owner "YOUR_GITHUB_USERNAME" \
  --repo-name "ai-release-guardian" \
  --pr-number 1 \
  --repo-path . \
  --output-dir ./demo_results

# Check results
cat demo_results/deployment_decision.json
```

**Step C2: Create Test PR**
```bash
git checkout -b demo/phase2-test

# Create demo test file
mkdir -p tests
cat > tests/test_demo.py << 'EOF'
"""Phase 2 Demo Tests"""
import pytest

def test_feature_one():
    """AC-1: Feature one works"""
    assert True

def test_feature_two():
    """AC-2: Feature two works"""
    assert True

def test_feature_three():
    """AC-3: Feature three works"""
    assert True

@pytest.mark.skip(reason="Demo: Not tested - coverage gap")
def test_untested_ac():
    """AC-4: Advanced feature (not tested)"""
    pass
EOF

# Commit and push
git add tests/test_demo.py
git commit -m "Demo: Add Phase 2 test scenarios"
git push origin demo/phase2-test
```

**Step C3: Create Pull Request**
```bash
gh pr create \
  --title "Demo: Phase 2 Automated QA Pipeline" \
  --body "This demonstrates Phase 2 functionality:
  
  - Phase 1: Tests generated + risk scored
  - Phase 2: Tests executed automatically
  - Phase 2: AC coverage validated
  - Phase 2: Deployment decision (GO/GATE/NO-GO)
  
  Watch the Actions tab for real-time progress!" \
  --base main \
  --head demo/phase2-test

# Note the PR number from output
```

**Step C4: Monitor Workflow**
```bash
# Watch in real-time
gh run watch

# Or check status periodically
watch -n 5 'gh run list --workflow phase2-release-guardian.yml --limit 3'

# Get detailed logs
gh run view <run-id> --log

# Check PR comment
gh pr view <pr-number> --comments
```

**Step C5: Test All Decision Paths**

**Path 1: GO Decision (Happy Path)**
- Already tested with demo PR above
- Expected: Auto-merge, all tests pass, coverage ≥80%

**Path 2: GATE Decision (Risky Changes)**
```bash
git checkout -b demo/gate-test

# Create simulated risky change
cat > src/db_migration.py << 'EOF'
"""Database schema migration - high risk"""
EOF

git add src/db_migration.py
git commit -m "Demo: DB migration (risky - expect GATE)"
git push origin demo/gate-test

gh pr create \
  --title "Demo: GATE Decision - Database Changes" \
  --base main \
  --head demo/gate-test

# Monitor → Should get GATE decision with DBA_REVIEW gate
```

**Path 3: NO-GO Decision (Failing Tests)**
```bash
git checkout -b demo/no-go-test

# Create failing test
cat > tests/test_fail.py << 'EOF'
def test_intentional_failure():
    """Demo: This test intentionally fails"""
    assert False, "This test is designed to fail"
EOF

git add tests/test_fail.py
git commit -m "Demo: Failing test (expect NO-GO)"
git push origin demo/no-go-test

gh pr create \
  --title "Demo: NO-GO Decision - Failing Tests" \
  --base main \
  --head demo/no-go-test

# Monitor → Should get NO-GO decision with failures listed
```

---

## 🔑 Getting Required API Keys

### Claude API Key
1. Go to https://console.anthropic.com/keys
2. Create new API key
3. Copy: `sk-ant-...`

### GitHub Token (if needed)
1. Go to https://github.com/settings/tokens
2. Create "Personal access token (classic)"
3. Scopes: repo, workflow
4. Copy: `ghp_...`

### Jira API Token (Optional)
1. Go to https://id.atlassian.com/manage-profile/security
2. Create API token
3. Copy token

---

## 📊 What to Expect at Each Stage

### After GitHub Setup
```
✅ Repository visible at https://github.com/YOUR_ORG/ai-release-guardian
✅ Workflow visible in Actions tab
✅ Secrets listed in Settings → Secrets
```

### After AWS Deployment
```
✅ Lambda function visible in AWS console
✅ CloudFormation stack shows "CREATE_COMPLETE"
✅ API Gateway endpoint accessible
✅ Environment variables configured
```

### During First PR
```
✅ GitHub Actions triggered automatically
✅ 5 jobs execute sequentially:
   1. Phase 1: Generate tests (30-60 sec)
   2. Phase 2: Execute tests (60-120 sec)
   3. Phase 2: Validate tests (10-20 sec)
   4. Phase 2: Make decision (5-10 sec)
   5. Publish results (5 sec)
✅ PR comment appears with decision
✅ Auto-merge (if GO) or blocked (if NO-GO)
```

---

## 🎯 Key Metrics to Track

### Performance
| Metric | Target | Measurement |
|--------|--------|-------------|
| Workflow time | <3 min | Time from PR to decision |
| Test execution | <2 min | Phase 2A duration |
| Decision time | <30 sec | Phase 2C duration |

### Quality
| Metric | Target | Measurement |
|--------|--------|-------------|
| Test pass rate | >95% | tests_executed.json |
| AC coverage | ≥80% | tests_validated.json |
| Decision accuracy | >99% | Compare AI vs actual |

### Automation
| Metric | Target | Measurement |
|--------|--------|-------------|
| Auto-merge rate | >90% | GO decisions / total |
| Manual review | <10% | GATE decisions / total |
| Blocked PRs | <5% | NO-GO decisions / total |

---

## 🔍 Troubleshooting Quick Reference

| Issue | Solution |
|-------|----------|
| Workflow not triggering | Check secrets set, workflow file committed |
| Tests not running | Check pytest installed, test files exist |
| Lambda timeout | Increase timeout in template.yaml |
| API not accessible | Check Lambda execution role permissions |
| Decision not posted | Check GitHub token is valid |
| Auto-merge not working | Check branch protection rules |

See `DEPLOYMENT_AND_DEMO_PLAN.md` for detailed troubleshooting.

---

## 📚 Documentation Quick Links

| Document | Purpose |
|----------|---------|
| `QUICK_START_DEPLOYMENT.md` | **START HERE** - Step-by-step setup |
| `DEPLOYMENT_AND_DEMO_PLAN.md` | Comprehensive deployment guide |
| `ARCHITECTURE_DEPLOYMENT.md` | Visual system architecture |
| `docs/PHASE2_GUIDE.md` | Phase 2 deep-dive |
| `docs/PHASE2_QUICK_REFERENCE.md` | Commands reference |

---

## ✅ Success Checklist

Print or copy this and check off as you complete each phase:

```
PHASE A: GitHub Setup
  [ ] Repository created on GitHub
  [ ] Code pushed to main branch
  [ ] CLAUDE_API_KEY secret set
  [ ] JIRA_API_TOKEN secret set (optional)
  [ ] Workflow visible in Actions tab
  [ ] All secrets listed in Settings

PHASE B: AWS Deployment  
  [ ] AWS credentials configured
  [ ] S3 bucket created
  [ ] SAM project built
  [ ] Lambda function deployed
  [ ] API endpoint obtained
  [ ] Environment variables configured
  [ ] Lambda function visible in AWS console

PHASE C: Demonstration
  [ ] Local end-to-end test passed
  [ ] Test PR created on GitHub
  [ ] Workflow triggered on PR
  [ ] Phase 1 job completed
  [ ] Phase 2A job completed
  [ ] Phase 2B job completed
  [ ] Phase 2C job completed
  [ ] PR comment posted with decision
  [ ] GO decision tested (auto-merge works)
  [ ] GATE decision tested (gates posted)
  [ ] NO-GO decision tested (merge blocked)
  [ ] Metrics collected and documented

FINAL VERIFICATION
  [ ] All workflows complete in <3 minutes
  [ ] All decision paths demonstrated
  [ ] Team trained on outcomes
  [ ] Metrics show QA velocity improvement
  [ ] Ready for production deployment
```

---

## 🚀 Ready to Start?

1. **Read**: `QUICK_START_DEPLOYMENT.md` (5 minutes)
2. **Follow**: Step-by-step instructions in order
3. **Track**: Use checklist above to mark progress
4. **Troubleshoot**: Reference `DEPLOYMENT_AND_DEMO_PLAN.md`

**Timeline:** ~2.5 hours total
**Difficulty:** Medium (requires GitHub & AWS setup)
**Result:** Fully automated AI-powered QA pipeline! ✨

---

## 🎓 Learning Path

After successful deployment, continue with:

1. **Monitor & Optimize**
   - Track decision accuracy over time
   - Adjust thresholds based on outcomes
   - Measure QA velocity improvements

2. **Expand**
   - Deploy to additional repositories
   - Share learnings with team
   - Build dashboard for metrics

3. **Phase 3 Planning**
   - Performance test automation
   - Security test automation
   - Advanced analytics

---

**Version:** 2.0 - Complete Phase 1 + Phase 2
**Status:** Ready for Deployment
**Date:** February 2026

**Start here:** → `QUICK_START_DEPLOYMENT.md`
