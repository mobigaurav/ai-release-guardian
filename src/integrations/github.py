"""GitHub API integration."""

import os
from typing import Optional, List
from github import Github, Repository, PullRequest
from src.utils import logger


class GitHubClient:
    """GitHub API wrapper for PR analysis."""
    
    def __init__(self, token: Optional[str] = None):
        """Initialize GitHub client."""
        self.token = token or os.getenv("GITHUB_TOKEN")
        if not self.token:
            raise ValueError("GITHUB_TOKEN not set in environment")
        
        self.client = Github(self.token)
        self._logger = logger
    
    def get_pr_diff(self, repo_owner: str, repo_name: str, pr_number: int) -> dict:
        """Get PR diff and file changes."""
        try:
            repo = self.client.get_user(repo_owner).get_repo(repo_name)
            pr = repo.get_pull(pr_number)
            
            files_changed = []
            for file in pr.get_files():
                files_changed.append({
                    "filename": file.filename,
                    "status": file.status,
                    "additions": file.additions,
                    "deletions": file.deletions,
                    "patch": file.patch or "",
                    "changes": file.changes,
                })
            
            return {
                "pr_number": pr_number,
                "title": pr.title,
                "body": pr.body or "",
                "author": pr.user.login,
                "base_branch": pr.base.ref,
                "head_branch": pr.head.ref,
                "files": files_changed,
                "total_files": len(files_changed),
                "total_additions": sum(f["additions"] for f in files_changed),
                "total_deletions": sum(f["deletions"] for f in files_changed),
            }
        except Exception as e:
            self._logger.error("Error fetching PR diff", error=str(e), pr_number=pr_number)
            raise
    
    def post_pr_comment(self, repo_owner: str, repo_name: str, pr_number: int, comment: str) -> dict:
        """Post a comment on a PR."""
        try:
            repo = self.client.get_user(repo_owner).get_repo(repo_name)
            pr = repo.get_pull(pr_number)
            
            comment_obj = pr.create_issue_comment(comment)
            
            self._logger.info("Posted PR comment", pr_number=pr_number, comment_id=comment_obj.id)
            
            return {
                "comment_id": comment_obj.id,
                "url": comment_obj.html_url,
            }
        except Exception as e:
            self._logger.error("Error posting PR comment", error=str(e), pr_number=pr_number)
            raise
    
    def extract_jira_tickets_from_pr(self, pr_title: str, pr_body: str) -> List[str]:
        """Extract Jira ticket IDs from PR title and body."""
        import re
        
        # Pattern: PROJECT-NUMBER (e.g., PROJ-123, INFRA-45)
        pattern = r'\b([A-Z][A-Z0-9]*-\d+)\b'
        
        combined_text = f"{pr_title}\n{pr_body}"
        matches = re.findall(pattern, combined_text)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_tickets = []
        for ticket in matches:
            if ticket not in seen:
                seen.add(ticket)
                unique_tickets.append(ticket)
        
        return unique_tickets


def create_github_client(token: Optional[str] = None) -> GitHubClient:
    """Factory function to create GitHub client."""
    return GitHubClient(token)
