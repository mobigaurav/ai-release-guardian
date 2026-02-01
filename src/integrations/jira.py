"""Jira API integration."""

import os
from typing import Optional, List, Dict
from jira import JIRA
from src.utils import logger


class JiraClient:
    """Jira API wrapper for ticket and AC retrieval."""
    
    def __init__(self, url: Optional[str] = None, user: Optional[str] = None, token: Optional[str] = None):
        """Initialize Jira client."""
        self.url = url or os.getenv("JIRA_URL")
        self.user = user or os.getenv("JIRA_USER")
        self.token = token or os.getenv("JIRA_API_TOKEN")
        
        if not all([self.url, self.user, self.token]):
            raise ValueError("Jira credentials not fully set in environment")
        
        self.client = JIRA(
            server=self.url,
            basic_auth=(self.user, self.token)
        )
        self._logger = logger
    
    def get_ticket_details(self, ticket_id: str) -> dict:
        """Get Jira ticket details including acceptance criteria."""
        try:
            issue = self.client.issue(ticket_id)
            
            # Extract acceptance criteria from description
            description = issue.fields.description or ""
            acceptance_criteria = self._extract_ac_from_description(description)
            
            return {
                "ticket_id": ticket_id,
                "key": issue.key,
                "summary": issue.fields.summary,
                "description": description,
                "status": issue.fields.status.name,
                "type": issue.fields.issuetype.name,
                "assignee": issue.fields.assignee.displayName if issue.fields.assignee else "Unassigned",
                "acceptance_criteria": acceptance_criteria,
                "labels": [label for label in issue.fields.labels],
                "priority": issue.fields.priority.name if issue.fields.priority else "Medium",
            }
        except Exception as e:
            self._logger.error("Error fetching Jira ticket", error=str(e), ticket_id=ticket_id)
            raise
    
    def get_multiple_tickets(self, ticket_ids: List[str]) -> List[dict]:
        """Get details for multiple Jira tickets."""
        results = []
        for ticket_id in ticket_ids:
            try:
                result = self.get_ticket_details(ticket_id)
                results.append(result)
            except Exception as e:
                self._logger.warning("Skipping ticket", error=str(e), ticket_id=ticket_id)
                continue
        
        return results
    
    def _extract_ac_from_description(self, description: str) -> List[str]:
        """Extract acceptance criteria from Jira description."""
        import re
        
        ac_list = []
        
        # Look for "Acceptance Criteria" section
        patterns = [
            r'(?:Acceptance Criteria|AC)[\s\n:]*([^*-]*(?:[*-][^\n]*)*)',
            r'(?:Given|When|Then)([^\n]*)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, description, re.IGNORECASE | re.MULTILINE)
            ac_list.extend(matches)
        
        # Clean up and filter
        cleaned_ac = []
        for ac in ac_list:
            ac = ac.strip().strip('*').strip('-').strip()
            if ac and len(ac) > 10:  # Only meaningful AC
                cleaned_ac.append(ac)
        
        return list(set(cleaned_ac))  # Remove duplicates


def create_jira_client(url: Optional[str] = None, user: Optional[str] = None, token: Optional[str] = None) -> JiraClient:
    """Factory function to create Jira client."""
    return JiraClient(url, user, token)
