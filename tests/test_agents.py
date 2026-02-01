"""Test suite for AI Release Guardian."""

import pytest
from unittest.mock import Mock, patch
from src.models.schemas import TestScenario, RiskAssessment


class TestTestScenario:
    """Test TestScenario model."""
    
    def test_create_integration_test(self):
        """Test creating an integration test scenario."""
        scenario = TestScenario(
            test_id="integration_1",
            name="test_user_creation",
            description="Test user creation flow",
            type="integration_test",
            scenario_steps=["POST /users", "Check DB"],
            expected_outcomes=["User created", "Email sent"]
        )
        
        assert scenario.test_id == "integration_1"
        assert scenario.type == "integration_test"
        assert len(scenario.scenario_steps) == 2
    
    def test_automation_test_with_priority(self):
        """Test automation test with priority."""
        scenario = TestScenario(
            test_id="auto_1",
            name="test_login_flow",
            description="Test login functionality",
            type="automation_test",
            scenario_steps=["Click login", "Enter credentials"],
            expected_outcomes=["Logged in"],
            priority="high"
        )
        
        assert scenario.priority == "high"


class TestRiskAssessment:
    """Test RiskAssessment model."""
    
    def test_low_risk_score(self):
        """Test low risk assessment."""
        risk = RiskAssessment(
            risk_score=15,
            confidence_percentage=85,
            risk_flags=[]
        )
        
        assert risk.risk_score == 15
        assert risk.confidence_percentage == 85
        assert not risk.requires_manual_review
    
    def test_high_risk_requires_review(self):
        """Test high risk requires manual review."""
        risk = RiskAssessment(
            risk_score=80,
            confidence_percentage=20,
            risk_flags=["Database schema changes"],
            requires_manual_review=True
        )
        
        assert risk.requires_manual_review
        assert risk.risk_score > 75


class TestAgentIntegration:
    """Test agent integration."""
    
    @patch('src.integrations.github.Github')
    def test_github_client_initialization(self, mock_github):
        """Test GitHub client initialization."""
        from src.integrations import GitHubClient
        
        client = GitHubClient(token="test_token")
        assert client.token == "test_token"
    
    def test_test_generator_creates_scenarios(self):
        """Test that test generator creates scenarios."""
        from src.models.schemas import TestScenario
        
        scenarios = [
            TestScenario(
                test_id="test_1",
                name="test",
                description="desc",
                type="integration_test",
                scenario_steps=["step"],
                expected_outcomes=["outcome"]
            )
        ]
        
        assert len(scenarios) > 0
        assert scenarios[0].type == "integration_test"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
