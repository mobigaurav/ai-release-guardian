"""Planner Agent - Analyzes PRs and Jira context."""

from typing import Optional, List
from src.integrations import GitHubClient, JiraClient
from src.utils import logger


class PlannerAgent:
    """Orchestrates PR and Jira analysis to create execution plan."""
    
    def __init__(self, github_client: GitHubClient, jira_client: Optional[JiraClient] = None):
        """Initialize planner agent."""
        self.github = github_client
        self.jira = jira_client
        self._logger = logger
    
    def analyze_pr_context(self, 
                          repo_owner: str, 
                          repo_name: str, 
                          pr_number: int) -> dict:
        """Analyze PR and gather all context."""
        try:
            # Get PR details
            pr_info = self.github.get_pr_diff(repo_owner, repo_name, pr_number)
            self._logger.info("PR info retrieved", pr_number=pr_number)
            
            # Extract Jira tickets
            jira_tickets = self.github.extract_jira_tickets_from_pr(
                pr_info["title"],
                pr_info["body"]
            )
            self._logger.info("Jira tickets extracted", tickets=jira_tickets)
            
            # Get Jira AC if available
            acceptance_criteria = []
            jira_details = {}
            
            if self.jira and jira_tickets:
                jira_details_list = self.jira.get_multiple_tickets(jira_tickets)
                jira_details = {ticket["ticket_id"]: ticket for ticket in jira_details_list}
                
                # Aggregate AC from all tickets
                for ticket_info in jira_details_list:
                    acceptance_criteria.extend(ticket_info.get("acceptance_criteria", []))
            
            # Classify files by type
            file_types = self._classify_files(pr_info["files"])
            
            return {
                "pr_info": pr_info,
                "jira_tickets": jira_tickets,
                "jira_details": jira_details,
                "acceptance_criteria": list(set(acceptance_criteria)),  # Unique AC
                "file_types": file_types,
                "total_changes": pr_info["total_additions"] + pr_info["total_deletions"],
            }
        except Exception as e:
            self._logger.error("Error in PR context analysis", error=str(e), pr_number=pr_number)
            raise
    
    def _classify_files(self, files: List[dict]) -> dict:
        """Classify modified files by type."""
        classification = {
            "backend": [],
            "frontend": [],
            "database": [],
            "infrastructure": [],
            "config": [],
            "tests": [],
            "other": [],
        }
        
        for file_info in files:
            filename = file_info["filename"].lower()
            
            if "test" in filename or "spec" in filename:
                classification["tests"].append(filename)
            elif any(ext in filename for ext in [".sql", ".migration", ".ddl"]):
                classification["database"].append(filename)
            elif any(ext in filename for ext in [".tf", ".yaml", ".yml", "docker", "k8s"]):
                classification["infrastructure"].append(filename)
            elif any(ext in filename for ext in [".json", ".toml", ".env", "config"]):
                classification["config"].append(filename)
            elif any(ext in filename for ext in [".js", ".jsx", ".tsx", ".ts", ".vue", ".css"]):
                classification["frontend"].append(filename)
            elif any(ext in filename for ext in [".py", ".go", ".java", ".rs", ".cpp", ".c"]):
                classification["backend"].append(filename)
            else:
                classification["other"].append(filename)
        
        return {k: v for k, v in classification.items() if v}  # Only return non-empty categories
    
    def extract_risky_patterns(self, pr_diff: str, file_types: dict) -> List[str]:
        """Identify risky change patterns."""
        risks = []
        
        # Check for database changes
        if file_types.get("database"):
            risks.append("Database schema changes detected - requires migration testing")
        
        # Check for auth changes
        if any("auth" in f.lower() for f in file_types.get("backend", []) + file_types.get("frontend", [])):
            risks.append("Authentication/Authorization changes - test all auth flows")
        
        # Check for API changes
        if any("api" in f.lower() or "route" in f.lower() for f in file_types.get("backend", [])):
            risks.append("API changes detected - verify contract compatibility")
        
        # Check for infrastructure
        if file_types.get("infrastructure"):
            risks.append("Infrastructure changes - requires DevOps review")
        
        # Check diff for breaking changes
        if "breaking" in pr_diff.lower() or "deprecated" in pr_diff.lower():
            risks.append("Breaking changes in code - versioning strategy check needed")
        
        return risks


def create_planner_agent(github_client: GitHubClient, 
                        jira_client: Optional[JiraClient] = None) -> PlannerAgent:
    """Factory function to create planner agent."""
    return PlannerAgent(github_client, jira_client)
