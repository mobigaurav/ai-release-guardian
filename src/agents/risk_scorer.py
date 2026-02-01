"""Risk Scorer Agent - Assesses release risk and confidence."""

from typing import Dict, List
from src.integrations import ClaudeAnalyzer
from src.models.schemas import RiskAssessment
from src.utils import logger


class RiskScorerAgent:
    """Scores release risk and identifies mitigation steps."""
    
    def __init__(self, claude_analyzer: ClaudeAnalyzer):
        """Initialize risk scorer agent."""
        self.claude = claude_analyzer
        self._logger = logger
    
    def score_release(self,
                     changes_summary: str,
                     file_types: Dict[str, List[str]],
                     total_changes: int,
                     risky_patterns: List[str]) -> RiskAssessment:
        """Score the risk of a release."""
        try:
            # Get Claude's assessment
            assessment = self.claude.score_release_risk(
                changes_summary,
                list(file_types.keys()),
                total_changes
            )
            
            # Add detected patterns
            risk_factors = assessment.get("risk_factors", [])
            risk_factors.extend(risky_patterns)
            
            # Create RiskAssessment object
            risk_assessment = RiskAssessment(
                risk_score=assessment.get("risk_score", 50),
                confidence_percentage=assessment.get("confidence_percentage", 50),
                risk_flags=risk_factors,
                suggestions=assessment.get("recommendations", []),
                requires_manual_review=assessment.get("requires_manual_review", False)
            )
            
            self._logger.info(
                "Release risk scored",
                risk_score=risk_assessment.risk_score,
                confidence=risk_assessment.confidence_percentage,
                requires_review=risk_assessment.requires_manual_review
            )
            
            return risk_assessment
        except Exception as e:
            self._logger.error("Error scoring release risk", error=str(e))
            # Return high-risk default on error
            return RiskAssessment(
                risk_score=75,
                confidence_percentage=25,
                risk_flags=["Analysis failed - manual review required"],
                suggestions=["Please review PR manually"],
                requires_manual_review=True
            )
    
    def calculate_confidence_percentage(self, risk_score: float) -> float:
        """Calculate confidence percentage from risk score."""
        # Inverse relationship: lower risk = higher confidence
        return max(0, min(100, 100 - risk_score))
    
    def get_risk_level(self, risk_score: float) -> str:
        """Get human-readable risk level."""
        if risk_score <= 20:
            return "LOW"
        elif risk_score <= 50:
            return "MEDIUM"
        elif risk_score <= 75:
            return "HIGH"
        else:
            return "CRITICAL"
    
    def extract_deployment_gates(self, risk_assessment: RiskAssessment) -> List[str]:
        """Extract deployment gates based on risk."""
        gates = []
        
        if "Database" in str(risk_assessment.risk_flags):
            gates.append("Verify database backups are recent")
            gates.append("Run data migration tests")
        
        if "Auth" in str(risk_assessment.risk_flags):
            gates.append("Test all authentication flows")
            gates.append("Verify session management")
        
        if "API" in str(risk_assessment.risk_flags):
            gates.append("Verify API contract compatibility")
            gates.append("Test backward compatibility")
        
        if "Infrastructure" in str(risk_assessment.risk_flags):
            gates.append("Verify infrastructure availability")
            gates.append("Check monitoring and alerting")
        
        if risk_assessment.risk_score > 50:
            gates.append("Requires QA sign-off")
        
        if risk_assessment.risk_score > 75:
            gates.append("Requires product manager approval")
            gates.append("Have rollback plan ready")
        
        return gates
    
    def generate_remediation_steps(self, 
                                   risk_assessment: RiskAssessment,
                                   acceptance_criteria: List[str]) -> List[str]:
        """Generate steps to mitigate identified risks."""
        steps = []
        
        # Add Claude's recommendations
        steps.extend(risk_assessment.suggestions)
        
        # Add AC-based checks
        for ac in acceptance_criteria:
            if "performance" in ac.lower():
                steps.append("Run performance benchmarks before and after")
            if "security" in ac.lower():
                steps.append("Run security scanning and SAST analysis")
            if "database" in ac.lower():
                steps.append("Validate database integrity post-deployment")
        
        # Generic steps for all deployments
        if not steps:
            steps = [
                "Run full integration test suite",
                "Perform smoke tests in staging",
                "Monitor error rates post-deployment",
            ]
        
        return steps


def create_risk_scorer_agent(claude_analyzer: ClaudeAnalyzer) -> RiskScorerAgent:
    """Factory function to create risk scorer agent."""
    return RiskScorerAgent(claude_analyzer)
