# Deployment Architecture & Flow Diagram

## Complete System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         DEVELOPER WORKFLOW                              │
└─────────────────────────────────────────────────────────────────────────┘

1. Developer creates feature branch and commits code
   └─> git checkout -b feature/my-feature
       git add .
       git commit -m "Feature: Add new capability"
       git push origin feature/my-feature

2. Developer creates Pull Request on GitHub
   └─> gh pr create --title "My Feature"
       └─> PR appears at: https://github.com/YOUR_ORG/ai-release-guardian/pull/X

3. GitHub webhook triggers immediately on PR open
   └─> Event: pull_request opened
       └─> Webhook URL: GitHub Actions (built-in)


┌─────────────────────────────────────────────────────────────────────────┐
│                    GITHUB ACTIONS WORKFLOW TRIGGER                      │
└─────────────────────────────────────────────────────────────────────────┘

Workflow: phase2-release-guardian.yml
Location: .github/workflows/phase2-release-guardian.yml
Trigger: Pull request opened/updated/reopened
Runner: ubuntu-latest


┌─────────────────────────────────────────────────────────────────────────┐
│                    PHASE 1: TEST GENERATION JOB                         │
│                     (Runs on: ubuntu-latest)                            │
└─────────────────────────────────────────────────────────────────────────┘

Job: phase1-test-generation
Duration: 30-60 seconds

Steps:
1. Checkout code
   └─> actions/checkout@v3 (fetch full history)

2. Setup Python 3.11
   └─> actions/setup-python@v4
   └─> With caching (pip cache)

3. Install dependencies
   └─> pip install -r requirements.txt

4. Generate tests & score risk
   └─> python -m src.agents.phase2_orchestrator generate-tests
   └─> Uses: Planner, TestGenerator, RiskScorer agents
   └─> Inputs: GitHub PR analysis + Jira AC extraction
   └─> Outputs: 
       ├─ tests_generated.json (test scenarios)
       ├─ risk_assessment.json (risk score + flags)
       └─ Artifacts uploaded

Flow:
   [GitHub PR diff] → [Planner] → [Analyze changes]
        ↓
   [Jira AC] → [Extract requirements]
        ↓
   [TestGenerator] → [Generate test scenarios via Claude]
        ↓
   [RiskScorer] → [Score risk level 0-100]
        ↓
   [tests_generated.json] → [Upload artifact]


┌─────────────────────────────────────────────────────────────────────────┐
│                    PHASE 2A: TEST EXECUTION JOB                         │
│              (Runs after Phase 1 successfully completes)                │
└─────────────────────────────────────────────────────────────────────────┘

Job: phase2-execute-tests
Depends on: phase1-test-generation
Duration: 60-120 seconds

Steps:
1. Checkout code

2. Setup Python & install dependencies
   └─> pip install -r requirements.txt
   └─> pip install pytest pytest-cov pytest-json-report

3. Execute tests
   └─> python -m src.agents.phase2_orchestrator execute-tests
   └─> Agent: TestExecutionAgent
   └─> Runs: pytest tests/ with JSON reporting
   └─> Captures:
       ├─ Total tests
       ├─ Passed/Failed/Errors
       ├─ Pass rate %
       ├─ Execution time
       └─ Coverage metrics

Flow:
   [Download artifact: tests_generated.json]
        ↓
   [Run pytest] → [Parse JSON report]
        ↓
   [Results: Pass/Fail/Error]
        ↓
   [tests_executed.json] → [Upload artifact]


┌─────────────────────────────────────────────────────────────────────────┐
│                   PHASE 2B: TEST VALIDATION JOB                         │
│             (Runs after Phase 2 Execute successfully completes)         │
└─────────────────────────────────────────────────────────────────────────┘

Job: phase2-validate-tests
Depends on: phase2-execute-tests
Duration: 10-20 seconds

Steps:
1. Download artifacts (tests_generated.json, tests_executed.json)

2. Validate tests
   └─> python -m src.agents.phase2_orchestrator validate-tests
   └─> Agent: TestValidationAgent
   └─> Validates:
       ├─ AC coverage % (target: ≥80%)
       ├─ Map tests to AC
       ├─ Identify coverage gaps
       └─ Validate test assertions

Flow:
   [Test results] + [Acceptance Criteria from Jira]
        ↓
   [Match test names to AC]
        ↓
   [Calculate coverage %]
        ├─ If ≥80%: Coverage PASS
        └─ If <80%: Coverage FAIL (gaps identified)
        ↓
   [tests_validated.json] → [Upload artifact]


┌─────────────────────────────────────────────────────────────────────────┐
│                   PHASE 2C: DEPLOYMENT DECISION JOB                     │
│             (Runs after Phase 2 Validate successfully completes)        │
└─────────────────────────────────────────────────────────────────────────┘

Job: phase2-deployment-decision
Depends on: phase2-validate-tests
Duration: 5-10 seconds

Steps:
1. Download all artifacts

2. Make deployment decision
   └─> python -m src.agents.phase2_orchestrator make-decision
   └─> Agent: DeploymentDecisionAgent
   └─> Decision Logic (7-tier):

Decision Logic Flow:
   
   1. Tests FAILED?
      ├─ YES → NO-GO ❌ (confidence 0%)
      └─ NO → Continue to 2

   2. AC Coverage < 80%?
      ├─ YES → NO-GO ❌ (confidence 0%)
      └─ NO → Continue to 3

   3. Validation FAILED?
      ├─ YES → NO-GO ❌ (confidence 0%)
      └─ NO → Continue to 4

   4. Risk ≥75 (CRITICAL)?
      ├─ YES → NO-GO ❌ (confidence 10%)
      └─ NO → Continue to 5

   5. Risk ≥50 + Database changes?
      ├─ YES → GATE ⚠️  (confidence 40%, gate: DBA_REVIEW)
      └─ NO → Continue to 6

   6. Risk ≥50 + other changes?
      ├─ YES → GATE ⚠️  (confidence 55%, gate: MANUAL_TESTING)
      └─ NO → Continue to 7

   7. All criteria pass?
      ├─ YES → GO ✅ (confidence = pass_rate × coverage × 100)
      └─ Should not reach here

Output:
   ├─ status: GO|GATE|NO-GO
   ├─ confidence: 0-100%
   ├─ reasoning: List of factors
   ├─ deployment_gates: Required approvals
   ├─ recommendation: Action to take
   └─ next_steps: Step-by-step instructions


┌─────────────────────────────────────────────────────────────────────────┐
│                    PHASE 2D: POST DECISION ACTIONS                      │
│                  (Conditional based on decision status)                 │
└─────────────────────────────────────────────────────────────────────────┘

Action 1: POST DECISION COMMENT TO PR
   └─> All decisions (GO/GATE/NO-GO)
   └─> Action: github-script
   └─> Posts formatted comment with:
       ├─ Decision status with emoji
       ├─ Tests executed count
       ├─ AC coverage %
       ├─ Risk assessment
       ├─ Reasoning
       ├─ Required gates (if any)
       ├─ Recommendation
       └─ Next steps

   Example Comment:
   ```
   ✅ Phase 2 - AI Release Guardian Auto-QA
   
   **Decision:** GO (Confidence: 92%)
   
   🧪 Tests Generated
   - Integration: 3
   - Automation: 2
   - E2E: 1
   - Total: 6
   
   ✅ Test Validation
   - AC Coverage: 85%
   - Status: PASS
   
   📊 Risk Assessment
   - Risk Score: 38/100 (LOW)
   - Risk Flags: None
   
   💡 Reasoning
   - 6/6 tests passed (100%)
   - 85% AC coverage ≥80% threshold
   - Risk score 38/100 (LOW) - no concerns
   
   🎯 Recommendation
   Deploy to production immediately. Auto-merge enabled.
   ```

Action 2: AUTO-MERGE (if GO decision)
   └─> Condition: status == "GO"
   └─> Action: Auto-merge PR
   └─> Method: squash merge
   └─> Result: PR merged automatically

Action 3: BLOCK MERGE (if NO-GO decision)
   └─> Condition: status == "NO-GO"
   └─> Action: Exit with error code 1
   └─> Result: GitHub prevents merge

Action 4: WAIT FOR APPROVAL (if GATE decision)
   └─> Condition: status == "GATE"
   └─> Action: Post gates in comment
   └─> Result: Manual approval required


┌─────────────────────────────────────────────────────────────────────────┐
│                   PHASE 2E: RESULTS PUBLICATION                         │
│                  (Runs after all jobs complete)                         │
└─────────────────────────────────────────────────────────────────────────┘

Job: publish-results
Runs: Always (even if previous jobs fail)

Actions:
1. Download all artifacts
2. Display summary in job logs
3. Make artifacts available for download
4. Send notifications (optional)


┌─────────────────────────────────────────────────────────────────────────┐
│                    WORKFLOW COMPLETION OUTCOMES                         │
└─────────────────────────────────────────────────────────────────────────┘

Scenario 1: GO Decision ✅
   ├─ All tests passed
   ├─ AC coverage ≥80%
   ├─ Risk score low
   ├─ PR auto-merged
   └─ Code automatically deployed to staging

Scenario 2: GATE Decision ⚠️
   ├─ Tests passed but risk detected
   ├─ PR comment posts required gates
   ├─ Merge blocked until approved
   ├─ Team must approve gates (DBA, manual testing, etc.)
   └─ After approval, manual merge or re-push

Scenario 3: NO-GO Decision ❌
   ├─ Tests failed OR coverage <80% OR critical risk
   ├─ PR comment lists all failures
   ├─ Merge blocked
   ├─ Developer must fix issues
   └─ On new push, workflow re-runs


┌─────────────────────────────────────────────────────────────────────────┐
│                      AWS LAMBDA DEPLOYMENT                              │
│                    (Optional webhook integration)                       │
└─────────────────────────────────────────────────────────────────────────┘

Deployment:
1. SAM template (lambda/template.yaml)
2. Build: sam build
3. Deploy: sam deploy
4. Result: Lambda function + API Gateway

GitHub Webhook Integration:
   [GitHub Event] → [Webhook POST to API Gateway]
                        ↓
                   [Lambda Function]
                        ↓
                   [Handler invokes agents]
                        ↓
                   [Results posted to GitHub]

Lambda Handler Flow:
   [GitHub webhook payload]
        ↓
   [Extract PR info]
        ↓
   [Invoke Phase 1 agents]
        ├─ Planner
        ├─ TestGenerator
        ├─ RiskScorer
        └─ Rollback (optional)
        ↓
   [Post analysis to PR]
        ↓
   [Return response to GitHub]


┌─────────────────────────────────────────────────────────────────────────┐
│                      COMPLETE DATA FLOW                                 │
└─────────────────────────────────────────────────────────────────────────┘

PR Created
   ↓
[1] GitHub Actions triggered
   ├─ Checkout code
   ├─ Setup environment
   └─ Install dependencies
   ↓
[2] PHASE 1 - Test Generation
   ├─ Analyze PR diff
   ├─ Extract Jira AC
   ├─ Generate test scenarios
   ├─ Score risk
   └─ Output: tests_generated.json
   ↓
[3] PHASE 2A - Test Execution
   ├─ Run pytest
   ├─ Parse results
   ├─ Capture coverage
   └─ Output: tests_executed.json
   ↓
[4] PHASE 2B - Test Validation
   ├─ Validate AC coverage
   ├─ Identify gaps
   ├─ Calculate statistics
   └─ Output: tests_validated.json
   ↓
[5] PHASE 2C - Deployment Decision
   ├─ Evaluate all criteria
   ├─ Apply decision logic
   ├─ Score confidence
   └─ Output: deployment_decision.json
   ↓
[6] Post Results
   ├─ Comment on PR
   ├─ Auto-merge if GO
   ├─ Block if NO-GO
   └─ Gate if GATE
   ↓
PR Status Updated
   └─ Decision visible to developer


┌─────────────────────────────────────────────────────────────────────────┐
│                      MONITORING & METRICS                               │
└─────────────────────────────────────────────────────────────────────────┘

Collect:
├─ Workflow execution time (target: <3 min)
├─ Test coverage % (target: ≥80%)
├─ Pass rate % (target: ≥95%)
├─ Decision distribution (GO/GATE/NO-GO)
├─ Auto-merge rate (target: ≥90%)
├─ Average PR time-to-merge (target: <5 min)
└─ Cost savings vs manual QA

Track Over Time:
├─ Decision accuracy (AI vs actual outcomes)
├─ Risk score correlation (does high risk = more bugs?)
├─ Team feedback on thresholds
└─ Iterate on decision logic


┌─────────────────────────────────────────────────────────────────────────┐
│                      SUCCESS INDICATORS                                 │
└─────────────────────────────────────────────────────────────────────────┘

✅ System is working if:
   ├─ GitHub Actions workflow triggers on every PR
   ├─ All 5 jobs complete successfully
   ├─ PR comment appears with decision (GO/GATE/NO-GO)
   ├─ GO decisions result in auto-merge
   ├─ NO-GO decisions block merge
   ├─ GATE decisions post gates and block merge
   ├─ Workflow completes in <3 minutes
   ├─ All agents execute without errors
   ├─ Coverage metrics calculated correctly
   └─ Decisions match expected outcomes

```

---

## Timeline Overview

```
T+0s:   PR created → GitHub Actions triggered
T+10s:  Phase 1 starts (test generation)
T+60s:  Phase 2A starts (test execution)
T+120s: Phase 2B starts (test validation)
T+130s: Phase 2C starts (deployment decision)
T+140s: Post decision and auto-merge (if GO)
T+150s: Workflow complete, results available

Total: ~2.5 minutes end-to-end
```

---

## Component Interactions

```
GitHub
  ├─ Stores code
  ├─ Runs Actions workflow
  ├─ Receives webhook (optional)
  └─ Posts PR comments

Workflow
  ├─ Phase 1 Agents
  │  ├─ Planner (PR analysis)
  │  ├─ TestGenerator (AI-powered)
  │  └─ RiskScorer (AI-powered)
  │
  ├─ Phase 2 Agents
  │  ├─ TestExecutor (pytest)
  │  ├─ TestValidator (AC coverage)
  │  └─ DeploymentDecider (GO/GATE/NO-GO)
  │
  └─ Orchestrator
     └─ Coordinates all agents

AWS (Optional)
  ├─ Lambda (webhook handler)
  ├─ API Gateway (HTTPS endpoint)
  └─ CloudFormation (infrastructure)

External APIs
  ├─ GitHub API (fetch PR info)
  ├─ Jira API (fetch AC)
  └─ Claude API (AI analysis)
```

---

**Architecture Version:** 2.0 (Phase 1 + Phase 2)
**Date:** February 2026
**Status:** Ready for Production Deployment
