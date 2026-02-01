"""Test Generator Agent - Creates integration and automation tests."""

from typing import List, Optional
from src.integrations import ClaudeAnalyzer
from src.models.schemas import TestScenario
from src.utils import logger


class TestGeneratorAgent:
    """Generates integration and automation test scenarios."""
    
    def __init__(self, claude_analyzer: ClaudeAnalyzer):
        """Initialize test generator agent."""
        self.claude = claude_analyzer
        self._logger = logger
    
    def generate_tests(self,
                      code_diff: str,
                      acceptance_criteria: List[str],
                      file_types: dict,
                      pr_title: str) -> dict:
        """Generate integration and automation tests."""
        try:
            # Get Claude's suggestions
            test_suggestions = self.claude.generate_test_scenarios(
                code_diff,
                acceptance_criteria,
                list(file_types.keys())
            )
            
            # Convert to TestScenario objects
            integration_tests = self._convert_to_test_scenarios(
                test_suggestions.get("integration_tests", []),
                test_type="integration_test"
            )
            
            automation_tests = self._convert_to_test_scenarios(
                test_suggestions.get("automation_tests", []),
                test_type="automation_test"
            )
            
            e2e_flows = self._convert_to_test_scenarios(
                test_suggestions.get("e2e_flows", []),
                test_type="e2e_test"
            )
            
            all_tests = integration_tests + automation_tests + e2e_flows
            
            self._logger.info(
                "Tests generated",
                integration_count=len(integration_tests),
                automation_count=len(automation_tests),
                e2e_count=len(e2e_flows),
                total=len(all_tests)
            )
            
            return {
                "integration_tests": integration_tests,
                "automation_tests": automation_tests,
                "e2e_flows": e2e_flows,
                "total_tests": len(all_tests),
                "raw_suggestions": test_suggestions
            }
        except Exception as e:
            self._logger.error("Error generating tests", error=str(e))
            return {
                "integration_tests": [],
                "automation_tests": [],
                "e2e_flows": [],
                "total_tests": 0,
                "error": str(e)
            }
    
    def _convert_to_test_scenarios(self, 
                                   tests: List[dict],
                                   test_type: str) -> List[TestScenario]:
        """Convert Claude suggestions to TestScenario objects."""
        scenarios = []
        
        for idx, test in enumerate(tests):
            try:
                scenario = TestScenario(
                    test_id=f"{test_type}_{idx + 1}",
                    name=test.get("name", f"Test {idx + 1}"),
                    description=test.get("description", ""),
                    type=test_type,
                    scenario_steps=test.get("steps", test.get("scenario", [])),
                    expected_outcomes=test.get("expected_outcomes", test.get("assertions", [])),
                    priority=test.get("priority", "medium"),
                    risk_flags=[]
                )
                scenarios.append(scenario)
            except Exception as e:
                self._logger.warning("Failed to convert test scenario", error=str(e), test=test)
                continue
        
        return scenarios
    
    def prioritize_tests(self, tests: List[TestScenario]) -> List[TestScenario]:
        """Sort tests by priority."""
        priority_order = {"high": 0, "medium": 1, "low": 2}
        return sorted(
            tests,
            key=lambda t: priority_order.get(t.priority, 99)
        )
    
    def generate_test_code_skeleton(self, test_scenario: TestScenario) -> str:
        """Generate Python test code skeleton."""
        if test_scenario.type == "integration_test":
            return self._generate_integration_test_code(test_scenario)
        elif test_scenario.type == "automation_test":
            return self._generate_automation_test_code(test_scenario)
        else:
            return self._generate_e2e_test_code(test_scenario)
    
    def _generate_integration_test_code(self, scenario: TestScenario) -> str:
        """Generate integration test code."""
        code = f'''
import pytest
from app import app
from database import db

@pytest.fixture
def client():
    """Test client fixture."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_{scenario.test_id}(client):
    """
    {scenario.description}
    
    Scenario:
    {chr(10).join(f"    - {step}" for step in scenario.scenario_steps)}
    
    Expected:
    {chr(10).join(f"    - {outcome}" for outcome in scenario.expected_outcomes)}
    """
    # TODO: Implement test logic
    # Arrange: Set up test data
    
    # Act: Perform the action
    
    # Assert: Verify results
    assert True  # Replace with actual assertions
'''
        return code
    
    def _generate_automation_test_code(self, scenario: TestScenario) -> str:
        """Generate automation test code."""
        code = f'''
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_{scenario.test_id}():
    """
    {scenario.description}
    
    Flow:
    {chr(10).join(f"    {i+1}. {step}" for i, step in enumerate(scenario.scenario_steps))}
    """
    driver = webdriver.Chrome()
    try:
        # TODO: Implement automation steps
        
        # Expected outcomes verification
        {chr(10).join(f"        # {outcome}" for outcome in scenario.expected_outcomes)}
        
        assert True  # Replace with actual assertions
    finally:
        driver.quit()
'''
        return code
    
    def _generate_e2e_test_code(self, scenario: TestScenario) -> str:
        """Generate E2E test code."""
        code = f'''
import pytest
from app import app
from database import db

@pytest.mark.e2e
def test_{scenario.test_id}():
    """
    E2E: {scenario.description}
    
    User Journey:
    {chr(10).join(f"    {i+1}. {step}" for i, step in enumerate(scenario.scenario_steps))}
    
    Verification:
    {chr(10).join(f"    ✓ {outcome}" for outcome in scenario.expected_outcomes)}
    """
    with app.test_client() as client:
        # TODO: Execute full user journey
        
        assert True  # Replace with actual assertions
'''
        return code


def create_test_generator_agent(claude_analyzer: ClaudeAnalyzer) -> TestGeneratorAgent:
    """Factory function to create test generator agent."""
    return TestGeneratorAgent(claude_analyzer)
