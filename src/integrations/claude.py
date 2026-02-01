"""Claude AI integration for intelligent analysis."""

import os
from typing import Optional
import anthropic
from src.utils import logger


class ClaudeAnalyzer:
    """Claude AI wrapper for PR and code analysis."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-5-sonnet-20241022"):
        """Initialize Claude client."""
        self.api_key = api_key or os.getenv("CLAUDE_API_KEY")
        if not self.api_key:
            raise ValueError("CLAUDE_API_KEY not set in environment")
        
        self.model = model
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self._logger = logger
    
    def analyze_pr_diff(self, diff: str, pr_title: str, acceptance_criteria: list) -> dict:
        """Analyze PR diff and generate insights."""
        prompt = f"""You are an expert QA engineer analyzing a GitHub PR.

PR Title: {pr_title}

Acceptance Criteria (from Jira):
{chr(10).join(f"- {ac}" for ac in acceptance_criteria)}

PR Diff:
{diff}

Please analyze this PR and provide:
1. Key changes and their impact
2. Integration points that need testing
3. Potential risks or edge cases
4. Files that were modified

Respond in JSON format:
{{
  "key_changes": ["change1", "change2"],
  "integration_points": ["point1", "point2"],
  "risks": ["risk1", "risk2"],
  "files_modified": ["file1", "file2"]
}}
"""
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            import json
            result = json.loads(response.content[0].text)
            return result
        except Exception as e:
            self._logger.error("Error analyzing PR diff", error=str(e))
            return {
                "key_changes": [],
                "integration_points": [],
                "risks": [],
                "files_modified": []
            }
    
    def generate_test_scenarios(self, 
                               code_diff: str, 
                               acceptance_criteria: list,
                               file_types: list) -> dict:
        """Generate integration and automation test scenarios."""
        prompt = f"""You are an expert test automation engineer.

Acceptance Criteria:
{chr(10).join(f"- {ac}" for ac in acceptance_criteria)}

Code Changes:
{code_diff}

File Types Modified: {', '.join(file_types)}

Generate comprehensive integration and automation test scenarios based on the acceptance criteria and code changes.

Respond with a JSON object:
{{
  "integration_tests": [
    {{
      "name": "test_name",
      "description": "what this tests",
      "steps": ["step1", "step2"],
      "expected_outcomes": ["outcome1", "outcome2"],
      "priority": "high|medium|low"
    }}
  ],
  "automation_tests": [
    {{
      "name": "test_name",
      "description": "what this tests",
      "scenario": ["action1", "action2"],
      "assertions": ["assert1", "assert2"],
      "priority": "high|medium|low"
    }}
  ],
  "e2e_flows": [
    {{
      "name": "user_journey_name",
      "description": "what user journey this tests",
      "steps": ["step1", "step2"],
      "data_setup": ["setup1", "setup2"]
    }}
  ]
}}

Focus on practical, executable tests that cover the acceptance criteria."""
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            import json
            result = json.loads(response.content[0].text)
            return result
        except Exception as e:
            self._logger.error("Error generating test scenarios", error=str(e))
            return {
                "integration_tests": [],
                "automation_tests": [],
                "e2e_flows": []
            }
    
    def score_release_risk(self, 
                          changes_summary: str,
                          file_types: list,
                          change_magnitude: int) -> dict:
        """Score the risk of a release."""
        prompt = f"""You are an expert release manager assessing deployment risk.

Changes Summary: {changes_summary}

File Types: {', '.join(file_types)}

Lines Changed: {change_magnitude}

Assess the risk of deploying this PR to production. Consider:
- Database schema changes
- API contract changes
- Authentication/Authorization changes
- Infrastructure changes
- Breaking changes
- Data migrations

Respond with JSON:
{{
  "risk_score": 0-100,
  "confidence_percentage": 0-100,
  "risk_factors": ["factor1", "factor2"],
  "recommendations": ["rec1", "rec2"],
  "requires_manual_review": true|false,
  "deployment_gates": ["gate1", "gate2"]
}}

Risk Score: 0-20=low, 21-50=medium, 51-75=high, 76-100=critical
Confidence: likelihood that this deployment will succeed"""
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1500,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            import json
            result = json.loads(response.content[0].text)
            return result
        except Exception as e:
            self._logger.error("Error scoring release risk", error=str(e))
            return {
                "risk_score": 50,
                "confidence_percentage": 50,
                "risk_factors": ["analysis_error"],
                "recommendations": ["manual_review_required"],
                "requires_manual_review": True,
                "deployment_gates": []
            }


def create_claude_analyzer(api_key: Optional[str] = None) -> ClaudeAnalyzer:
    """Factory function to create Claude analyzer."""
    return ClaudeAnalyzer(api_key)
