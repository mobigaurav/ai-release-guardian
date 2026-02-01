"""AWS Lambda handler for GitHub webhooks."""

import json
import os
import logging
from src.integrations import (
    create_github_client,
    create_jira_client,
    create_claude_analyzer
)
from src.agents import (
    create_planner_agent,
    create_test_generator_agent,
    create_risk_scorer_agent,
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """
    AWS Lambda handler for GitHub PR webhooks.
    
    Triggered by GitHub webhook on PR opened/synchronize events.
    """
    try:
        # Parse webhook payload
        body = json.loads(event.get("body", "{}"))
        
        if body.get("action") not in ["opened", "synchronize"]:
            return {"statusCode": 200, "body": "Webhook ignored"}
        
        pr = body.get("pull_request", {})
        repo = body.get("repository", {})
        
        pr_number = pr.get("number")
        repo_owner = repo.get("owner", {}).get("login")
        repo_name = repo.get("name")
        
        logger.info(f"Processing PR #{pr_number} in {repo_owner}/{repo_name}")
        
        if not all([pr_number, repo_owner, repo_name]):
            return {"statusCode": 400, "body": "Invalid webhook payload"}
        
        # Initialize clients
        github_client = create_github_client()
        jira_client = create_jira_client() if os.getenv("JIRA_API_TOKEN") else None
        claude_analyzer = create_claude_analyzer()
        
        # Create agents
        planner = create_planner_agent(github_client, jira_client)
        test_gen = create_test_generator_agent(claude_analyzer)
        risk_scorer = create_risk_scorer_agent(claude_analyzer)
        
        # Analyze PR
        context = planner.analyze_pr_context(repo_owner, repo_name, pr_number)
        pr_info = context["pr_info"]
        
        # Generate tests
        test_result = test_gen.generate_tests(
            "\n".join([f["patch"] for f in pr_info["files"]]),
            context["acceptance_criteria"],
            context["file_types"],
            pr_info["title"]
        )
        
        # Score risk
        risky_patterns = planner.extract_risky_patterns(
            "\n".join([f["patch"] for f in pr_info["files"]]),
            context["file_types"]
        )
        
        risk = risk_scorer.score_release(
            pr_info["title"],
            context["file_types"],
            context["total_changes"],
            risky_patterns
        )
        
        # Generate PR comment
        comment_body = _generate_pr_comment(
            test_result,
            risk,
            context
        )
        
        # Post comment to GitHub
        github_client.post_pr_comment(repo_owner, repo_name, pr_number, comment_body)
        
        logger.info(f"Successfully processed PR #{pr_number}")
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "success": True,
                "pr_number": pr_number,
                "tests_generated": test_result["total_tests"],
                "risk_score": risk.risk_score,
            })
        }
    
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }


def _generate_pr_comment(test_result: dict, risk, context: dict) -> str:
    """Generate a GitHub PR comment with analysis results."""
    
    # Risk level badge
    risk_level = _get_risk_level(risk.risk_score)
    risk_emoji = "🟢" if risk_level == "LOW" else "🟡" if risk_level == "MEDIUM" else "🔴"
    
    # Test summary
    tests_summary = f"""
### 🧪 Auto-Generated Test Scenarios ({test_result['total_tests']} total)

**Integration Tests:** {len(test_result['integration_tests'])} ✓
**Automation Tests:** {len(test_result['automation_tests'])} ✓
**E2E Flows:** {len(test_result['e2e_flows'])} ✓
"""
    
    if test_result['integration_tests']:
        tests_summary += "\n#### Integration Tests:\n"
        for test in test_result['integration_tests'][:3]:  # Show top 3
            tests_summary += f"- **{test.name}**: {test.description}\n"
    
    # Risk assessment
    risk_summary = f"""
### {risk_emoji} Release Risk Assessment

**Risk Score:** {risk.risk_score}/100 ({risk_level})
**Deployment Confidence:** {risk.confidence_percentage}%
**Manual Review Required:** {'Yes ⚠️' if risk.requires_manual_review else 'No ✓'}

#### Risk Flags:
{chr(10).join(f'- ⚠️ {flag}' for flag in risk.risk_flags[:5])}
"""
    
    # Jira context
    jira_summary = ""
    if context['jira_tickets']:
        jira_summary = f"\n### 📋 Linked Jira Tickets\n"
        jira_summary += f"{', '.join(context['jira_tickets'])}\n"
        if context['acceptance_criteria']:
            jira_summary += "\n#### Acceptance Criteria:\n"
            jira_summary += "\n".join(f"- {ac}" for ac in context['acceptance_criteria'][:5])
    
    # Suggestions
    suggestions = f"\n### 💡 Recommendations\n"
    suggestions += "\n".join(f"- {s}" for s in risk.suggestions[:5])
    
    comment = f"""## 🤖 AI Release Guardian Analysis

{tests_summary}

{risk_summary}

{jira_summary}

{suggestions}

---
*Generated by AI Release Guardian - Phase 1*
"""
    
    return comment


def _get_risk_level(risk_score: float) -> str:
    """Get risk level from score."""
    if risk_score <= 20:
        return "LOW"
    elif risk_score <= 50:
        return "MEDIUM"
    elif risk_score <= 75:
        return "HIGH"
    else:
        return "CRITICAL"
