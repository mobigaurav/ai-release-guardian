"""Test Executor Agent - Runs generated tests and captures results."""

import subprocess
import json
from typing import Optional, List, Dict
from pathlib import Path
from src.utils import logger


class TestExecutionAgent:
    """Executes generated test scenarios and captures results."""
    
    def __init__(self):
        """Initialize test executor agent."""
        self._logger = logger
    
    def execute_tests(self, repo_path: str, test_pattern: str = "tests/") -> dict:
        """
        Execute tests using pytest and capture results.
        
        Args:
            repo_path: Path to repository
            test_pattern: Test file pattern to run
        
        Returns:
            Dictionary with test results
        """
        self._logger.info("Executing tests", repo_path=repo_path)
        
        results = {
            "timestamp": str(__import__('datetime').datetime.now()),
            "repo_path": repo_path,
            "tests": [],
            "summary": {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "errors": 0,
                "pass_rate": 0.0,
                "execution_time_seconds": 0
            },
            "status": "SUCCESS"
        }
        
        try:
            # Run pytest with JSON report
            cmd = [
                "pytest",
                f"{repo_path}/{test_pattern}",
                "-v",
                "--tb=short",
                "--json-report",
                "--json-report-file=/tmp/test_report.json",
                "--junit-xml=/tmp/junit.xml"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            # Parse JSON report
            try:
                with open("/tmp/test_report.json") as f:
                    report = json.load(f)
                    results = self._parse_pytest_report(report, results)
            except FileNotFoundError:
                # Fallback: parse stdout if JSON report not available
                results = self._parse_pytest_output(result.stdout, results)
            
            # Check if any tests failed
            if results["summary"]["failed"] > 0 or results["summary"]["errors"] > 0:
                results["status"] = "FAILED"
            
            self._logger.info(
                "Tests executed",
                total=results["summary"]["total"],
                passed=results["summary"]["passed"],
                failed=results["summary"]["failed"]
            )
            
        except subprocess.TimeoutExpired:
            self._logger.error("Test execution timeout")
            results["status"] = "TIMEOUT"
            results["summary"]["errors"] = 1
        except Exception as e:
            self._logger.error("Error executing tests", error=str(e))
            results["status"] = "ERROR"
            results["summary"]["errors"] = 1
        
        return results
    
    def _parse_pytest_report(self, report: dict, results: dict) -> dict:
        """Parse pytest JSON report."""
        summary = report.get("summary", {})
        tests = report.get("tests", [])
        
        results["summary"]["total"] = summary.get("total", 0)
        results["summary"]["passed"] = summary.get("passed", 0)
        results["summary"]["failed"] = summary.get("failed", 0)
        results["summary"]["skipped"] = summary.get("skipped", 0)
        results["summary"]["errors"] = summary.get("error", 0)
        results["summary"]["execution_time_seconds"] = summary.get("duration", 0)
        
        if results["summary"]["total"] > 0:
            results["summary"]["pass_rate"] = results["summary"]["passed"] / results["summary"]["total"]
        
        # Parse individual tests
        for test in tests:
            test_result = {
                "name": test.get("nodeid", ""),
                "status": test.get("outcome", "unknown"),
                "duration": test.get("duration", 0),
                "error": test.get("call", {}).get("longrepr", "") if test.get("outcome") == "failed" else ""
            }
            results["tests"].append(test_result)
        
        return results
    
    def _parse_pytest_output(self, stdout: str, results: dict) -> dict:
        """Fallback: parse pytest stdout."""
        lines = stdout.split('\n')
        
        # Extract summary line
        for line in lines:
            if 'passed' in line or 'failed' in line:
                # Parse pytest summary line
                if 'passed' in line:
                    try:
                        passed = int(line.split('passed')[0].split()[-1])
                        results["summary"]["passed"] = passed
                    except:
                        pass
                if 'failed' in line:
                    try:
                        failed = int(line.split('failed')[0].split()[-1])
                        results["summary"]["failed"] = failed
                    except:
                        pass
        
        # Calculate totals
        results["summary"]["total"] = results["summary"]["passed"] + results["summary"]["failed"]
        if results["summary"]["total"] > 0:
            results["summary"]["pass_rate"] = results["summary"]["passed"] / results["summary"]["total"]
        
        return results
    
    def run_integration_tests(self, repo_path: str) -> dict:
        """Run integration tests specifically."""
        self._logger.info("Running integration tests")
        return self.execute_tests(repo_path, test_pattern="tests/test_integrations.py")
    
    def run_unit_tests(self, repo_path: str) -> dict:
        """Run unit tests specifically."""
        self._logger.info("Running unit tests")
        return self.execute_tests(repo_path, test_pattern="tests/test_agents.py")
    
    def generate_test_report(self, test_results: dict, output_file: str = "test_report.json") -> str:
        """Generate and save test report."""
        with open(output_file, 'w') as f:
            json.dump(test_results, f, indent=2)
        
        self._logger.info("Test report generated", file=output_file)
        return output_file


def create_test_executor_agent() -> TestExecutionAgent:
    """Factory function to create test executor agent."""
    return TestExecutionAgent()
