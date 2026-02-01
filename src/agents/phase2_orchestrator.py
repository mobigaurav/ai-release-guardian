"""Phase 2 Orchestrator - Orchestrates all Phase 1 & Phase 2 agents."""

import json
import sys
from pathlib import Path
from typing import Optional

from src.agents.planner import create_planner_agent
from src.agents.test_generator import create_test_generator_agent
from src.agents.risk_scorer import create_risk_scorer_agent
from src.agents.test_executor import create_test_executor_agent
from src.agents.test_validator import create_test_validator_agent
from src.agents.deployment_decider import create_deployment_decision_agent
from src.integrations import create_github_client, create_jira_client, create_claude_analyzer
from src.utils import logger


class Phase2Orchestrator:
    """Orchestrates Phase 1 + Phase 2 agents for end-to-end QA automation."""
    
    def __init__(self):
        """Initialize orchestrator."""
        self.github = create_github_client()
        self.jira = create_jira_client() if __import__('os').getenv("JIRA_API_TOKEN") else None
        self.claude = create_claude_analyzer()
        
        self.planner = create_planner_agent(self.github, self.jira)
        self.test_gen = create_test_generator_agent(self.claude)
        self.risk_scorer = create_risk_scorer_agent(self.claude)
        self.test_executor = create_test_executor_agent()
        self.test_validator = create_test_validator_agent()
        self.deployment_decider = create_deployment_decision_agent()
        
        self._logger = logger
    
    def generate_tests(self, repo_owner: str, repo_name: str, pr_number: int, 
                      output_file: str = "tests_generated.json") -> dict:
        """
        Phase 1: Generate tests and score risk.
        
        Returns:
            Generated tests and risk assessment
        """
        self._logger.info("Phase 1: Generating tests", pr_number=pr_number)
        
        # Analyze PR
        context = self.planner.analyze_pr_context(repo_owner, repo_name, pr_number)
        pr_info = context["pr_info"]
        
        # Generate tests
        tests = self.test_gen.generate_tests(
            "\n".join([f["patch"] for f in pr_info["files"]]),
            context["acceptance_criteria"],
            context["file_types"],
            pr_info["title"]
        )
        
        # Score risk
        risky_patterns = self.planner.extract_risky_patterns(
            "\n".join([f["patch"] for f in pr_info["files"]]),
            context["file_types"]
        )
        
        risk = self.risk_scorer.score_release(
            pr_info["title"],
            context["file_types"],
            context["total_changes"],
            risky_patterns
        )
        
        # Aggregate results
        output = {
            "pr_number": pr_number,
            "pr_title": pr_info["title"],
            "tests": {
                "integration": [t.dict() for t in tests["integration_tests"]],
                "automation": [t.dict() for t in tests["automation_tests"]],
                "e2e": [t.dict() for t in tests["e2e_flows"]],
                "total": tests["total_tests"]
            },
            "risk_assessment": {
                "risk_score": risk.risk_score,
                "confidence_percentage": risk.confidence_percentage,
                "risk_flags": risk.risk_flags,
                "suggestions": risk.suggestions,
                "requires_manual_review": risk.requires_manual_review
            },
            "jira_context": {
                "tickets": context["jira_tickets"],
                "acceptance_criteria": context["acceptance_criteria"]
            },
            "file_types": context["file_types"]
        }
        
        # Save output
        with open(output_file, 'w') as f:
            json.dump(output, f, indent=2)
        
        self._logger.info("Tests generated and saved", file=output_file, total=tests["total_tests"])
        return output
    
    def execute_tests(self, repo_path: str, output_file: str = "tests_executed.json") -> dict:
        """
        Phase 2: Execute generated tests.
        
        Returns:
            Test execution results
        """
        self._logger.info("Phase 2: Executing tests", repo_path=repo_path)
        
        # Run tests
        results = self.test_executor.execute_tests(repo_path)
        
        # Save output
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        self._logger.info("Tests executed and saved", file=output_file, passed=results["summary"]["passed"])
        return results
    
    def validate_tests(self, test_results_file: str, repo_owner: str, 
                      repo_name: str, pr_number: int,
                      output_file: str = "tests_validated.json") -> dict:
        """
        Phase 2: Validate tests against AC.
        
        Returns:
            Validation report
        """
        self._logger.info("Phase 2: Validating tests")
        
        # Load test results
        with open(test_results_file) as f:
            test_results = json.load(f)
        
        # Get PR context for AC
        context = self.planner.analyze_pr_context(repo_owner, repo_name, pr_number)
        
        # Validate
        validation = self.test_validator.validate_tests(
            test_results,
            context["acceptance_criteria"],
            coverage_requirement=80
        )
        
        # Save output
        with open(output_file, 'w') as f:
            json.dump(validation, f, indent=2)
        
        self._logger.info("Tests validated and saved", file=output_file, status=validation["status"])
        return validation
    
    def make_decision(self, test_defs_file: str, test_results_file: str, 
                     validation_report_file: str, 
                     output_file: str = "deployment_decision.json") -> dict:
        """
        Phase 2: Make deployment decision.
        
        Returns:
            Deployment decision with GO/GATE/NO-GO status
        """
        self._logger.info("Phase 2: Making deployment decision")
        
        # Load all reports
        with open(test_defs_file) as f:
            test_defs = json.load(f)
        with open(test_results_file) as f:
            test_results = json.load(f)
        with open(validation_report_file) as f:
            validation = json.load(f)
        
        # Make decision
        decision = self.deployment_decider.make_decision(
            test_results,
            validation,
            test_defs["risk_assessment"]
        )
        
        # Save output
        with open(output_file, 'w') as f:
            json.dump(decision, f, indent=2)
        
        self._logger.info("Decision made and saved", file=output_file, status=decision["status"])
        return decision
    
    def end_to_end(self, repo_owner: str, repo_name: str, pr_number: int, 
                   repo_path: str, output_dir: str = ".") -> dict:
        """
        Run complete Phase 1 + Phase 2 pipeline.
        
        Returns:
            Final decision and all intermediate results
        """
        self._logger.info("Running end-to-end Phase 1 + Phase 2 pipeline", pr_number=pr_number)
        
        # Phase 1: Generate tests
        test_defs = self.generate_tests(
            repo_owner, repo_name, pr_number,
            f"{output_dir}/phase1_tests_generated.json"
        )
        
        # Phase 2: Execute tests
        test_results = self.execute_tests(
            repo_path,
            f"{output_dir}/phase2_tests_executed.json"
        )
        
        # Phase 2: Validate tests
        validation = self.validate_tests(
            f"{output_dir}/phase2_tests_executed.json",
            repo_owner, repo_name, pr_number,
            f"{output_dir}/phase2_tests_validated.json"
        )
        
        # Phase 2: Make decision
        decision = self.make_decision(
            f"{output_dir}/phase1_tests_generated.json",
            f"{output_dir}/phase2_tests_executed.json",
            f"{output_dir}/phase2_tests_validated.json",
            f"{output_dir}/phase2_deployment_decision.json"
        )
        
        # Aggregate results
        pipeline_result = {
            "pr_number": pr_number,
            "phase1_tests_generated": test_defs["tests"]["total"],
            "phase2_tests_executed": test_results["summary"]["total"],
            "phase2_tests_passed": test_results["summary"]["passed"],
            "phase2_ac_coverage": validation["coverage_percentage"],
            "phase2_deployment_decision": decision["status"],
            "phase2_confidence": decision["confidence"],
            "files": {
                "tests_generated": f"{output_dir}/phase1_tests_generated.json",
                "tests_executed": f"{output_dir}/phase2_tests_executed.json",
                "tests_validated": f"{output_dir}/phase2_tests_validated.json",
                "deployment_decision": f"{output_dir}/phase2_deployment_decision.json"
            }
        }
        
        self._logger.info(
            "End-to-end pipeline complete",
            decision_status=decision["status"],
            tests_passed=test_results["summary"]["passed"]
        )
        
        return pipeline_result


def create_phase2_orchestrator() -> Phase2Orchestrator:
    """Factory function to create Phase 2 orchestrator."""
    return Phase2Orchestrator()


def main():
    """CLI entry point for Phase 2 orchestrator."""
    import argparse
    
    parser = argparse.ArgumentParser(description="AI Release Guardian Phase 2 Orchestrator")
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Generate tests command
    gen = subparsers.add_parser('generate-tests', help='Phase 1: Generate tests')
    gen.add_argument('--repo-owner', required=True)
    gen.add_argument('--repo-name', required=True)
    gen.add_argument('--pr-number', type=int, required=True)
    gen.add_argument('--output', default='phase1_tests_generated.json')
    
    # Execute tests command
    exe = subparsers.add_parser('execute-tests', help='Phase 2: Execute tests')
    exe.add_argument('--repo-path', required=True)
    exe.add_argument('--output', default='phase2_tests_executed.json')
    
    # Validate tests command
    val = subparsers.add_parser('validate-tests', help='Phase 2: Validate tests')
    val.add_argument('--test-results', required=True)
    val.add_argument('--repo-owner', required=True)
    val.add_argument('--repo-name', required=True)
    val.add_argument('--pr-number', type=int, required=True)
    val.add_argument('--output', default='phase2_tests_validated.json')
    
    # Make decision command
    dec = subparsers.add_parser('make-decision', help='Phase 2: Make deployment decision')
    dec.add_argument('--test-defs', required=True)
    dec.add_argument('--test-results', required=True)
    dec.add_argument('--validation', required=True)
    dec.add_argument('--output', default='phase2_deployment_decision.json')
    
    # End-to-end command
    e2e = subparsers.add_parser('end-to-end', help='Run complete Phase 1 + Phase 2')
    e2e.add_argument('--repo-owner', required=True)
    e2e.add_argument('--repo-name', required=True)
    e2e.add_argument('--pr-number', type=int, required=True)
    e2e.add_argument('--repo-path', required=True)
    e2e.add_argument('--output-dir', default='.')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    orchestrator = create_phase2_orchestrator()
    
    try:
        if args.command == 'generate-tests':
            result = orchestrator.generate_tests(
                args.repo_owner, args.repo_name, args.pr_number, args.output
            )
            print(f"✓ Tests generated: {result['tests']['total']}")
        
        elif args.command == 'execute-tests':
            result = orchestrator.execute_tests(args.repo_path, args.output)
            print(f"✓ Tests executed: {result['summary']['passed']}/{result['summary']['total']} passed")
        
        elif args.command == 'validate-tests':
            result = orchestrator.validate_tests(
                args.test_results, args.repo_owner, args.repo_name, 
                args.pr_number, args.output
            )
            print(f"✓ Tests validated: {result['coverage_percentage']}% AC coverage")
        
        elif args.command == 'make-decision':
            result = orchestrator.make_decision(
                args.test_defs, args.test_results, args.validation, args.output
            )
            print(f"✓ Decision made: {result['status']}")
        
        elif args.command == 'end-to-end':
            result = orchestrator.end_to_end(
                args.repo_owner, args.repo_name, args.pr_number, 
                args.repo_path, args.output_dir
            )
            print(f"✓ Pipeline complete: {result['phase2_deployment_decision']}")
            print(f"  Tests: {result['phase2_tests_passed']}/{result['phase2_tests_executed']} passed")
            print(f"  AC Coverage: {result['phase2_ac_coverage']}%")
            print(f"  Confidence: {result['phase2_confidence']}%")
    
    except Exception as e:
        logger.error("Error in Phase 2 orchestrator", error=str(e))
        print(f"✗ Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
