"""Deployment Decision Agent - Makes GO/GATE/NO-GO deployment decisions."""

from typing import Dict, List, Optional
from src.utils import logger


class DeploymentDecisionAgent:
    """Makes deployment decisions based on aggregated test and risk data."""
    
    def __init__(self):
        """Initialize deployment decision agent."""
        self._logger = logger
    
    def make_decision(self,
                     test_results: Dict,
                     validation_report: Dict,
                     risk_assessment: Dict) -> Dict:
        """
        Make GO/GATE/NO-GO deployment decision.
        
        Decision Logic:
        - GO: Immediate deployment to staging
        - GATE: Requires manual review/approval
        - NO-GO: Block deployment, needs fixes
        
        Args:
            test_results: Test execution results
            validation_report: AC coverage validation
            risk_assessment: Release risk score & flags
        
        Returns:
            Deployment decision with reasoning
        """
        decision = {
            "timestamp": str(__import__('datetime').datetime.now()),
            "status": "GO",
            "confidence": 100,
            "reasoning": [],
            "deployment_gates": [],
            "recommendation": "",
            "next_steps": []
        }
        
        try:
            # Extract key metrics
            pass_rate = test_results["summary"].get("pass_rate", 0)
            test_status = test_results.get("status", "SUCCESS")
            coverage = validation_report.get("coverage_percentage", 0)
            validation_status = validation_report.get("status", "PASS")
            risk_score = risk_assessment.get("risk_score", 50)
            risk_flags = risk_assessment.get("risk_flags", [])
            
            self._logger.info(
                "Making deployment decision",
                pass_rate=pass_rate,
                coverage=coverage,
                risk_score=risk_score
            )
            
            # Rule 1: Test failures are hard blockers
            if test_status == "FAILED" or pass_rate < 1.0:
                decision["status"] = "NO-GO"
                decision["confidence"] = 0
                decision["reasoning"].append(
                    f"Tests failed: {test_results['summary'].get('failed', 0)} failures"
                )
                decision["recommendation"] = "Fix failing tests before deployment"
                decision["next_steps"].append("Review test failures")
                decision["next_steps"].append("Fix failing code")
                decision["next_steps"].append("Re-run tests")
            
            # Rule 2: AC coverage too low is a blocker
            elif coverage < 80:
                decision["status"] = "NO-GO"
                decision["confidence"] = 0
                decision["reasoning"].append(
                    f"AC coverage too low: {coverage}% < 80% requirement"
                )
                decision["recommendation"] = "Add tests to meet AC coverage requirement"
                decision["next_steps"].append("Identify missing AC tests")
                decision["next_steps"].append("Add test scenarios")
                decision["next_steps"].append("Validate coverage")
            
            # Rule 3: Validation failures are blockers
            elif validation_status == "FAIL":
                decision["status"] = "NO-GO"
                decision["confidence"] = 0
                decision["reasoning"].append("Test validation failed")
                decision["reasoning"].extend(validation_report.get("gaps", [])[:3])
                decision["recommendation"] = "Fix validation issues"
                decision["next_steps"].append("Review validation report")
                decision["next_steps"].append("Fix identified gaps")
            
            # Rule 4: Critical risk score requires blocking
            elif risk_score >= 75:
                decision["status"] = "NO-GO"
                decision["confidence"] = 10
                decision["reasoning"].append(
                    f"Critical risk score: {risk_score}/100"
                )
                decision["reasoning"].extend(risk_flags[:3])
                decision["recommendation"] = "Requires extensive review and testing"
                decision["deployment_gates"].append("Security team review required")
                decision["deployment_gates"].append("Architecture review required")
                decision["deployment_gates"].append("Load testing required")
                decision["next_steps"].append("Schedule security review")
                decision["next_steps"].append("Plan load testing")
            
            # Rule 5: High risk with DB changes needs gate
            elif risk_score >= 50 and "database" in [f.lower() for f in risk_flags]:
                decision["status"] = "GATE"
                decision["confidence"] = 40
                decision["reasoning"].append(
                    f"High risk with database changes: {risk_score}/100"
                )
                decision["reasoning"].append("Database migration detected")
                decision["deployment_gates"].append("DBA approval required")
                decision["deployment_gates"].append("Database backup verified")
                decision["deployment_gates"].append("Rollback procedure tested")
                decision["next_steps"].append("Contact DBA for review")
                decision["next_steps"].append("Verify backup strategy")
            
            # Rule 6: High risk with auth/API changes needs gate
            elif risk_score >= 50:
                decision["status"] = "GATE"
                decision["confidence"] = 55
                decision["reasoning"].append(
                    f"Medium-high risk: {risk_score}/100"
                )
                decision["reasoning"].extend(risk_flags[:2])
                decision["deployment_gates"].append("Manual testing recommended")
                decision["deployment_gates"].append("Staging validation required")
                decision["next_steps"].append("Run manual smoke tests in staging")
                decision["next_steps"].append("Verify user flows work correctly")
            
            # Rule 7: Good metrics = GO
            else:
                decision["status"] = "GO"
                decision["confidence"] = min(100, int(pass_rate * 100 * (coverage / 100)))
                decision["reasoning"].append(
                    f"Tests passed: {pass_rate*100:.0f}%"
                )
                decision["reasoning"].append(
                    f"AC coverage: {coverage}%"
                )
                decision["reasoning"].append(
                    f"Risk score: {risk_score}/100 (LOW)"
                )
                decision["recommendation"] = "Safe to deploy - all metrics look good"
                decision["next_steps"].append("Auto-merge to main")
                decision["next_steps"].append("Deploy to staging")
                decision["next_steps"].append("Monitor metrics")
            
            self._logger.info("Decision made", status=decision["status"], confidence=decision["confidence"])
            
        except Exception as e:
            self._logger.error("Error making decision", error=str(e))
            decision["status"] = "GATE"
            decision["confidence"] = 0
            decision["reasoning"].append(f"Decision logic error: {str(e)}")
            decision["recommendation"] = "Manual review required due to decision error"
        
        return decision
    
    def can_auto_merge(self, decision: Dict) -> bool:
        """Check if PR can be auto-merged."""
        return decision["status"] == "GO"
    
    def can_deploy_to_staging(self, decision: Dict) -> bool:
        """Check if safe to deploy to staging."""
        return decision["status"] in ["GO", "GATE"]
    
    def requires_manual_review(self, decision: Dict) -> bool:
        """Check if manual review is required."""
        return decision["status"] in ["GATE", "NO-GO"]
    
    def format_decision_summary(self, decision: Dict) -> str:
        """Format decision as human-readable string."""
        emoji = "✅" if decision["status"] == "GO" else \
                "⚠️" if decision["status"] == "GATE" else "❌"
        
        summary = f"{emoji} **{decision['status']}** (Confidence: {decision['confidence']}%)\n\n"
        
        summary += "**Reasoning:**\n"
        for reason in decision["reasoning"]:
            summary += f"- {reason}\n"
        
        if decision["deployment_gates"]:
            summary += "\n**Required Gates:**\n"
            for gate in decision["deployment_gates"]:
                summary += f"- ⚠️ {gate}\n"
        
        summary += f"\n**Recommendation:** {decision['recommendation']}\n"
        
        if decision["next_steps"]:
            summary += "\n**Next Steps:**\n"
            for i, step in enumerate(decision["next_steps"], 1):
                summary += f"{i}. {step}\n"
        
        return summary


def create_deployment_decision_agent() -> DeploymentDecisionAgent:
    """Factory function to create deployment decision agent."""
    return DeploymentDecisionAgent()
