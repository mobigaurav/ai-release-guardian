"""Test Validator Agent - Validates test results against acceptance criteria."""

from typing import List, Dict, Optional
from src.utils import logger


class TestValidationAgent:
    """Validates test results against acceptance criteria and coverage requirements."""
    
    def __init__(self):
        """Initialize test validator agent."""
        self._logger = logger
    
    def validate_tests(self, 
                      test_results: dict, 
                      acceptance_criteria: List[str],
                      coverage_requirement: float = 80.0) -> dict:
        """
        Validate tests against AC and coverage requirements.
        
        Args:
            test_results: Test execution results
            acceptance_criteria: List of AC from Jira
            coverage_requirement: Minimum coverage % required
        
        Returns:
            Validation report
        """
        validation = {
            "timestamp": str(__import__('datetime').datetime.now()),
            "ac_coverage": [],
            "coverage_percentage": 0,
            "gaps": [],
            "status": "PASS",
            "issues": [],
            "warnings": []
        }
        
        try:
            # Extract test names
            test_names = [t["name"].lower() for t in test_results.get("tests", [])]
            
            # Check each AC is tested
            for idx, ac in enumerate(acceptance_criteria):
                ac_lower = ac.lower()
                
                # Look for matching test
                matching_tests = [t for t in test_results["tests"] 
                                 if self._matches_ac(t["name"], ac)]
                
                if matching_tests:
                    # Check if tests passed
                    passed_tests = [t for t in matching_tests if t["status"] == "passed"]
                    
                    if passed_tests:
                        validation["ac_coverage"].append({
                            "ac": ac,
                            "tested": True,
                            "passed": True,
                            "test_count": len(passed_tests)
                        })
                    else:
                        validation["ac_coverage"].append({
                            "ac": ac,
                            "tested": True,
                            "passed": False,
                            "test_count": len(matching_tests)
                        })
                        validation["gaps"].append(f"Tests exist for AC but failed: {ac}")
                        validation["status"] = "FAIL"
                else:
                    validation["ac_coverage"].append({
                        "ac": ac,
                        "tested": False,
                        "passed": False,
                        "test_count": 0
                    })
                    validation["gaps"].append(f"No test found for AC: {ac}")
                    validation["warnings"].append(f"Missing coverage for: {ac}")
            
            # Calculate coverage
            tested_count = len([ac for ac in validation["ac_coverage"] if ac["tested"]])
            total_count = len(acceptance_criteria)
            
            if total_count > 0:
                coverage_pct = (tested_count / total_count) * 100
                validation["coverage_percentage"] = round(coverage_pct, 2)
            
            # Check coverage requirement
            if validation["coverage_percentage"] < coverage_requirement:
                validation["issues"].append(
                    f"AC Coverage {validation['coverage_percentage']}% < {coverage_requirement}% requirement"
                )
                validation["status"] = "FAIL"
            
            # Check test pass rate
            summary = test_results.get("summary", {})
            if summary.get("failed", 0) > 0:
                validation["issues"].append(
                    f"{summary['failed']} test(s) failed"
                )
                validation["status"] = "FAIL"
            
            if summary.get("errors", 0) > 0:
                validation["issues"].append(
                    f"{summary['errors']} test error(s)"
                )
                validation["status"] = "FAIL"
            
            # Check if any tests were run
            if summary.get("total", 0) == 0:
                validation["issues"].append("No tests were executed")
                validation["status"] = "FAIL"
            
            self._logger.info(
                "Tests validated",
                status=validation["status"],
                coverage=validation["coverage_percentage"]
            )
            
        except Exception as e:
            self._logger.error("Error validating tests", error=str(e))
            validation["status"] = "ERROR"
            validation["issues"].append(f"Validation error: {str(e)}")
        
        return validation
    
    def _matches_ac(self, test_name: str, ac: str) -> bool:
        """Check if test name matches AC description."""
        test_lower = test_name.lower()
        ac_lower = ac.lower()
        
        # Extract key words from AC
        ac_words = ac_lower.split()
        
        # Check if key words appear in test name
        matching_words = sum(1 for word in ac_words if word in test_lower and len(word) > 3)
        
        # If at least 2 meaningful words match, consider it matching
        return matching_words >= 2 or ac_lower in test_lower
    
    def validate_test_assertions(self, test_results: dict) -> dict:
        """Validate that tests have proper assertions."""
        validation = {
            "total_tests": len(test_results.get("tests", [])),
            "tests_with_errors": [],
            "status": "PASS"
        }
        
        for test in test_results.get("tests", []):
            if test.get("status") == "failed" and test.get("error"):
                validation["tests_with_errors"].append({
                    "test": test.get("name"),
                    "error": test.get("error")[:200]  # First 200 chars
                })
        
        if validation["tests_with_errors"]:
            validation["status"] = "FAIL"
        
        return validation
    
    def check_coverage_gaps(self, test_results: dict, acceptance_criteria: List[str]) -> List[str]:
        """Identify gaps in test coverage."""
        gaps = []
        
        test_names = [t["name"].lower() for t in test_results.get("tests", [])]
        
        for ac in acceptance_criteria:
            if not any(self._matches_ac(t, ac) for t in test_names):
                gaps.append(f"No test coverage for: {ac}")
        
        return gaps


def create_test_validator_agent() -> TestValidationAgent:
    """Factory function to create test validator agent."""
    return TestValidationAgent()
