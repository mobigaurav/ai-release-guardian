# Deployment Checklist - AI Release Guardian Phase 1

## Pre-Deployment Validation

### ✅ Local Testing (Dev Machine)
- [ ] Python 3.11+ installed
- [ ] Virtual environment created and activated
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] `.env` file created with all required keys
- [ ] MCP server starts: `python src/mcp/server.py`
- [ ] Health check passes: `curl http://localhost:8000/health`
- [ ] All tests pass: `pytest tests/ -v`

### ✅ API Validation
- [ ] `/health` endpoint returns 200
- [ ] `/generate-tests` accepts valid payload
- [ ] `/release-risk-score` returns risk score (0-100)
- [ ] `/analyze-release` requires repo_owner/repo_name/pr_number
- [ ] `/rollback-plan` generates steps

### ✅ External Services
- [ ] GitHub token is valid (test with: `curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/user`)
- [ ] Claude API key is valid (test in MCP server)
- [ ] Jira URL, user, and API token are valid (optional but recommended)
- [ ] No API rate limiting issues

### ✅ Code Quality
- [ ] No lint errors: `ruff check src/`
- [ ] Type hints are present: `mypy src/` (optional)
- [ ] Code formatted: `black src/`
- [ ] Unit tests pass with coverage > 70%

## AWS Lambda Deployment

### ✅ Pre-Deployment (AWS Account Setup)
- [ ] AWS account exists with appropriate permissions
- [ ] AWS CLI installed and configured: `aws configure`
- [ ] SAM CLI installed: `pip install aws-sam-cli`
- [ ] S3 bucket created for SAM deployment artifacts
- [ ] IAM role has Lambda execution permissions

### ✅ Build & Package
- [ ] Navigate to `lambda/` directory
- [ ] Lambda dependencies installed: `pip install -r lambda/requirements.txt`
- [ ] Lambda code tested locally (optional)
- [ ] Run: `sam build`
- [ ] Verify `build/` directory created

### ✅ Deployment
- [ ] Run SAM deploy with parameters:
  ```bash
  sam deploy \
    --parameter-overrides \
      GitHubToken=ghp_xxxxx \
      JiraUrl=https://your-jira.atlassian.net \
      JiraUser=your-email@company.com \
      JiraApiToken=xxxxx \
      ClaudeApiKey=sk-ant-xxxxx
  ```
- [ ] Deployment completes without errors
- [ ] Save output webhook URL
- [ ] Lambda function appears in AWS Console

### ✅ Post-Deployment (AWS Validation)
- [ ] Lambda function created: `ai-release-guardian`
- [ ] Environment variables set correctly in Lambda console
- [ ] CloudWatch logs group created: `/aws/lambda/ai-release-guardian`
- [ ] API Gateway endpoint created and accessible
- [ ] Test Lambda with test event payload

## GitHub Integration

### ✅ Webhook Setup
- [ ] Go to your repo: Settings → Webhooks
- [ ] Click "Add webhook"
- [ ] **Payload URL**: Paste the Lambda API Gateway URL from SAM output
- [ ] **Content type**: `application/json`
- [ ] **Events**: Select "Pull requests" → only "Pull request opened" and "Pull request synchronize"
- [ ] **Active**: ✅ checked
- [ ] Save webhook

### ✅ Test Webhook
- [ ] Create a test PR in your repo
- [ ] PR should trigger Lambda
- [ ] Check CloudWatch logs: `/aws/lambda/ai-release-guardian`
- [ ] Verify PR comment posted within 30 seconds
- [ ] Check comment has:
  - [ ] Test scenarios listed
  - [ ] Risk score displayed
  - [ ] Recommendations present

### ✅ Webhook Validation
- [ ] Webhook shows "Recent Deliveries" in GitHub
- [ ] No "Failed" deliveries
- [ ] Response codes are 200/202

## Monitoring & Observability

### ✅ CloudWatch Setup
- [ ] CloudWatch Logs group exists: `/aws/lambda/ai-release-guardian`
- [ ] Log retention set to appropriate level (30 days recommended)
- [ ] Logs contain expected messages (PR analysis, tests generated, risk scored)

### ✅ Alarms (Recommended)
- [ ] Lambda error rate alarm (threshold > 5%)
- [ ] Lambda timeout alarm (threshold > 55 seconds)
- [ ] Lambda concurrent execution alarm

### ✅ Testing Scenarios
- [ ] Test with simple PR (few files)
- [ ] Test with complex PR (many files)
- [ ] Test with database changes
- [ ] Test with API changes
- [ ] Test with auth changes
- [ ] Test with no Jira tickets
- [ ] Test with multiple Jira tickets

## Rollback Plan

### ✅ If Deployment Fails
1. [ ] Delete Lambda function: `aws lambda delete-function --function-name ai-release-guardian`
2. [ ] Delete API Gateway: `aws apigateway delete-rest-api --rest-api-id xxx`
3. [ ] Remove webhook from GitHub
4. [ ] Debug issue locally, repeat deployment

### ✅ If PR Comments Are Wrong
1. [ ] Check CloudWatch logs for errors
2. [ ] Verify API keys in Lambda environment variables
3. [ ] Test MCP server locally with same payloads
4. [ ] Update code if needed, redeploy

## Security Checklist

- [ ] API keys not committed to Git (check `.gitignore`)
- [ ] `.env` file in `.gitignore`
- [ ] Lambda function has minimal IAM permissions
- [ ] GitHub token has only `repo` scope (not admin)
- [ ] Jira API token is not exposed in logs
- [ ] CloudWatch logs are not publicly accessible

## Performance Verification

- [ ] Lambda execution time < 30 seconds (target)
- [ ] Memory usage < 512 MB
- [ ] Cold start < 10 seconds
- [ ] PR comment posted within 30-60 seconds of PR creation

## Documentation & Handoff

- [ ] README.md is up-to-date
- [ ] GETTING_STARTED.md covers deployment
- [ ] QUICK_REFERENCE.md is accessible
- [ ] Team knows how to:
  - [ ] Monitor CloudWatch logs
  - [ ] Update environment variables
  - [ ] Rollback if needed
  - [ ] Troubleshoot webhook issues

## Post-Deployment Monitoring (First Week)

- [ ] Monitor error logs daily
- [ ] Verify PR comments quality
- [ ] Check that tests are helpful to QA
- [ ] Gather feedback from QA team
- [ ] Document any issues encountered
- [ ] Plan Phase 2 improvements based on feedback

## Success Criteria

✅ **Deployment is successful when:**
1. PRs trigger Lambda automatically
2. PR comments post within 60 seconds
3. Comments contain meaningful test scenarios
4. Risk scores are reasonable (low risk for trivial changes, high for DB changes)
5. No errors in CloudWatch logs
6. QA team finds value in generated tests
7. Time-to-review metrics show improvement

---

## Deployment Timeline

| Phase | Duration | Notes |
|-------|----------|-------|
| Pre-deployment validation | 30 mins | Local testing |
| Lambda build & deployment | 10 mins | SAM deploy |
| GitHub webhook configuration | 5 mins | Manual setup |
| Initial testing | 20 mins | Create test PRs |
| Monitoring setup | 15 mins | CloudWatch, alerts |
| **Total** | **~1.5 hours** | First deployment |

---

**Ready to deploy?** Start with "Pre-Deployment Validation" checklist above.

**Having issues?** See GETTING_STARTED.md troubleshooting section.
