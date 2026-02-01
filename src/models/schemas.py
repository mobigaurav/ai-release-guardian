"""Data models and schemas."""

from typing import Optional, List
from pydantic import BaseModel, Field


class TestScenario(BaseModel):
    """Integration or automation test scenario."""
    
    test_id: str = Field(..., description="Unique test identifier")
    name: str = Field(..., description="Test name")
    description: str = Field(..., description="What the test validates")
    type: str = Field(..., description="integration_test or automation_test or e2e_test")
    scenario_steps: List[str] = Field(..., description="Step-by-step test flow")
    expected_outcomes: List[str] = Field(..., description="Expected results")
    risk_flags: List[str] = Field(default=[], description="Risky patterns detected")
    priority: str = Field(default="medium", description="high, medium, low")


class RiskAssessment(BaseModel):
    """Risk assessment for a PR."""
    
    risk_score: float = Field(..., ge=0, le=100, description="Risk score 0-100")
    confidence_percentage: float = Field(..., ge=0, le=100, description="Confidence in deployment")
    risk_flags: List[str] = Field(default=[], description="Detected risks")
    suggestions: List[str] = Field(default=[], description="Mitigation suggestions")
    requires_manual_review: bool = Field(default=False, description="Requires QA review")


class PRAnalysis(BaseModel):
    """Complete PR analysis result."""
    
    pr_number: int
    pr_title: str
    repo: str
    changed_files: List[str] = Field(default=[], description="Files modified in PR")
    jira_tickets: List[str] = Field(default=[], description="Linked Jira tickets")
    acceptance_criteria: List[str] = Field(default=[], description="AC from Jira")
    test_scenarios: List[TestScenario] = Field(default=[], description="Generated tests")
    risk_assessment: Optional[RiskAssessment] = None
    summary: str = Field(default="", description="Human-readable summary")


class RollbackPlan(BaseModel):
    """Rollback procedure for a release."""
    
    release_id: str
    steps: List[str] = Field(..., description="Rollback steps in order")
    estimated_duration_minutes: int = Field(..., description="Estimated time to rollback")
    critical_alerts: List[str] = Field(default=[], description="Things to monitor during rollback")
    data_backup_required: bool = Field(default=False, description="Need DB backup first")
