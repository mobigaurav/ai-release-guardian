"""MCP Server - Exposes Release Guardian capabilities."""

import os
import json
from typing import Optional
from flask import Flask, request, jsonify
from src.integrations import (
    create_github_client,
    create_jira_client,
    create_claude_analyzer
)
from src.agents import (
    create_planner_agent,
    create_test_generator_agent,
    create_risk_scorer_agent,
    create_rollback_planner_agent
)
from src.utils import logger, setup_logging


class ReleasGuardianMCPServer:
    """MCP server for Release Guardian."""
    
    def __init__(self):
        """Initialize MCP server."""
        setup_logging()
        self.app = Flask(__name__)
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup API routes."""
        
        @self.app.route("/health", methods=["GET"])
        def health():
            return jsonify({"status": "ok", "service": "ai-release-guardian"}), 200
        
        @self.app.route("/analyze-release", methods=["POST"])
        def analyze_release():
            """Analyze a release and generate recommendations."""
            try:
                data = request.json
                return self._analyze_release_impl(data)
            except Exception as e:
                logger.error("Error in analyze-release", error=str(e))
                return jsonify({"error": str(e)}), 400
        
        @self.app.route("/generate-tests", methods=["POST"])
        def generate_tests():
            """Generate integration and automation tests."""
            try:
                data = request.json
                return self._generate_tests_impl(data)
            except Exception as e:
                logger.error("Error in generate-tests", error=str(e))
                return jsonify({"error": str(e)}), 400
        
        @self.app.route("/release-risk-score", methods=["POST"])
        def release_risk_score():
            """Score the risk of a release."""
            try:
                data = request.json
                return self._release_risk_score_impl(data)
            except Exception as e:
                logger.error("Error in release-risk-score", error=str(e))
                return jsonify({"error": str(e)}), 400
        
        @self.app.route("/rollback-plan", methods=["POST"])
        def rollback_plan():
            """Generate rollback procedure."""
            try:
                data = request.json
                return self._rollback_plan_impl(data)
            except Exception as e:
                logger.error("Error in rollback-plan", error=str(e))
                return jsonify({"error": str(e)}), 400
    
    def _analyze_release_impl(self, data: dict) -> tuple:
        """Implementation of analyze-release endpoint."""
        repo_owner = data.get("repo_owner")
        repo_name = data.get("repo_name")
        pr_number = data.get("pr_number")
        
        if not all([repo_owner, repo_name, pr_number]):
            return jsonify({"error": "Missing required fields"}), 400
        
        # Initialize clients
        github_client = create_github_client()
        jira_client = create_jira_client() if os.getenv("JIRA_API_TOKEN") else None
        claude_analyzer = create_claude_analyzer()
        
        # Create agents
        planner = create_planner_agent(github_client, jira_client)
        test_gen = create_test_generator_agent(claude_analyzer)
        risk_scorer = create_risk_scorer_agent(claude_analyzer)
        
        # Analyze
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
        
        return jsonify({
            "success": True,
            "pr_number": pr_number,
            "analysis": {
                "files": pr_info["files"],
                "jira_tickets": context["jira_tickets"],
                "acceptance_criteria": context["acceptance_criteria"],
                "tests_generated": test_result["total_tests"],
                "risk_score": risk.risk_score,
                "confidence": risk.confidence_percentage,
                "risk_flags": risk.risk_flags,
                "requires_manual_review": risk.requires_manual_review,
            }
        }), 200
    
    def _generate_tests_impl(self, data: dict) -> tuple:
        """Implementation of generate-tests endpoint."""
        code_diff = data.get("code_diff")
        acceptance_criteria = data.get("acceptance_criteria", [])
        file_types = data.get("file_types", {})
        
        if not code_diff:
            return jsonify({"error": "Missing code_diff"}), 400
        
        claude_analyzer = create_claude_analyzer()
        test_gen = create_test_generator_agent(claude_analyzer)
        
        result = test_gen.generate_tests(
            code_diff,
            acceptance_criteria,
            file_types,
            data.get("pr_title", "")
        )
        
        return jsonify({
            "success": True,
            "integration_tests": [t.dict() for t in result["integration_tests"]],
            "automation_tests": [t.dict() for t in result["automation_tests"]],
            "e2e_flows": [t.dict() for t in result["e2e_flows"]],
            "total": result["total_tests"]
        }), 200
    
    def _release_risk_score_impl(self, data: dict) -> tuple:
        """Implementation of release-risk-score endpoint."""
        changes_summary = data.get("changes_summary")
        file_types = data.get("file_types", {})
        total_changes = data.get("total_changes", 0)
        
        if not changes_summary:
            return jsonify({"error": "Missing changes_summary"}), 400
        
        claude_analyzer = create_claude_analyzer()
        risk_scorer = create_risk_scorer_agent(claude_analyzer)
        
        risk = risk_scorer.score_release(
            changes_summary,
            file_types,
            total_changes,
            data.get("risky_patterns", [])
        )
        
        return jsonify({
            "success": True,
            "risk_score": risk.risk_score,
            "confidence_percentage": risk.confidence_percentage,
            "risk_flags": risk.risk_flags,
            "suggestions": risk.suggestions,
            "requires_manual_review": risk.requires_manual_review,
        }), 200
    
    def _rollback_plan_impl(self, data: dict) -> tuple:
        """Implementation of rollback-plan endpoint."""
        release_id = data.get("release_id")
        changed_files = data.get("changed_files", [])
        file_types = data.get("file_types", {})
        
        if not release_id:
            return jsonify({"error": "Missing release_id"}), 400
        
        planner = create_rollback_planner_agent()
        
        plan = planner.generate_rollback_plan(
            release_id,
            changed_files,
            file_types,
            data.get("risk_flags", [])
        )
        
        return jsonify({
            "success": True,
            "release_id": plan.release_id,
            "steps": plan.steps,
            "estimated_duration_minutes": plan.estimated_duration_minutes,
            "critical_alerts": plan.critical_alerts,
            "data_backup_required": plan.data_backup_required,
        }), 200
    
    def run(self, host: str = "0.0.0.0", port: int = 8000, debug: bool = False):
        """Run the MCP server."""
        logger.info("Starting Release Guardian MCP Server", host=host, port=port)
        self.app.run(host=host, port=port, debug=debug)


def main():
    """Main entry point."""
    server = ReleasGuardianMCPServer()
    port = int(os.getenv("MCP_SERVER_PORT", 8000))
    debug = os.getenv("ENV") == "development"
    server.run(port=port, debug=debug)


if __name__ == "__main__":
    main()
