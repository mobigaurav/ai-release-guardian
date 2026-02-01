"""Rollback Planner Agent - Creates rollback procedures."""

from typing import List, Dict
from src.models.schemas import RollbackPlan
from src.utils import logger


class RollbackPlannerAgent:
    """Generates rollback procedures for deployments."""
    
    def __init__(self):
        """Initialize rollback planner agent."""
        self._logger = logger
    
    def generate_rollback_plan(self,
                              release_id: str,
                              changed_files: List[str],
                              file_types: Dict[str, List[str]],
                              risk_flags: List[str]) -> RollbackPlan:
        """Generate a rollback procedure."""
        try:
            steps = []
            critical_alerts = []
            data_backup_required = False
            
            # Database changes require backup
            if file_types.get("database"):
                data_backup_required = True
                steps.append("✅ Backup most recent from pre-deployment state")
                steps.append("Revert database schema to previous version")
                steps.append("Run post-rollback data validation")
                critical_alerts.append("Database integrity check required")
            
            # Infrastructure changes
            if file_types.get("infrastructure"):
                steps.append("Scale down new infrastructure")
                steps.append("Restore previous infrastructure configuration")
                steps.append("Point traffic back to previous version")
                critical_alerts.append("DNS/Load balancer failover")
            
            # API/Backend changes
            if file_types.get("backend"):
                steps.append("Trigger deployment of previous version")
                steps.append("Clear application caches")
                steps.append("Verify service health checks passing")
                critical_alerts.append("API version compatibility")
            
            # Frontend changes
            if file_types.get("frontend"):
                steps.append("Clear CDN cache")
                steps.append("Deploy previous frontend version")
                steps.append("Verify UI loads correctly in all browsers")
            
            # Config changes
            if file_types.get("config"):
                steps.append("Rollback configuration management changes")
                steps.append("Restart services with previous config")
            
            # Add generic rollback steps
            if not steps:
                steps = [
                    "Revert to previous release version",
                    "Run post-rollback verification tests",
                    "Monitor error rates and user reports"
                ]
            
            # Add monitoring and validation
            steps.append("Monitor application metrics for 30 minutes")
            steps.append("Verify all integration tests passing")
            steps.append("Check error rates have returned to baseline")
            steps.append("Post-incident review with team")
            
            # Add critical alerts based on risk flags
            for flag in risk_flags:
                if "Auth" in flag:
                    critical_alerts.append("Verify authentication services operational")
                if "Payment" in flag:
                    critical_alerts.append("Verify payment processing available")
                if "Data" in flag:
                    critical_alerts.append("Verify data consistency")
            
            rollback_plan = RollbackPlan(
                release_id=release_id,
                steps=steps,
                estimated_duration_minutes=self._estimate_duration(file_types),
                critical_alerts=critical_alerts,
                data_backup_required=data_backup_required
            )
            
            self._logger.info("Rollback plan generated", release_id=release_id, steps=len(steps))
            return rollback_plan
        except Exception as e:
            self._logger.error("Error generating rollback plan", error=str(e))
            raise
    
    def _estimate_duration(self, file_types: Dict[str, List[str]]) -> int:
        """Estimate rollback duration in minutes."""
        base_time = 5
        
        if file_types.get("database"):
            base_time += 15
        
        if file_types.get("infrastructure"):
            base_time += 20
        
        if file_types.get("backend"):
            base_time += 10
        
        if file_types.get("frontend"):
            base_time += 5
        
        # Add buffer for verification
        base_time += 10
        
        return base_time
    
    def create_pre_deployment_checklist(self, rollback_plan: RollbackPlan) -> List[str]:
        """Create a pre-deployment checklist based on rollback plan."""
        checklist = [
            "☐ Rollback plan reviewed by team",
            "☐ Backups verified and tested",
            "☐ Communication channel open (Slack/incident channel)",
            "☐ Team members available during deployment window",
        ]
        
        if rollback_plan.data_backup_required:
            checklist.append("☐ Database backups confirmed and recent")
            checklist.append("☐ Backup restore procedure tested")
        
        checklist.extend([
            f"☐ {alert}" for alert in rollback_plan.critical_alerts
        ])
        
        return checklist
    
    def create_post_deployment_checklist(self, rollback_plan: RollbackPlan) -> List[str]:
        """Create post-deployment validation checklist."""
        return [
            "☐ All services reporting healthy status",
            "☐ Error rates within normal parameters",
            "☐ No critical alerts in monitoring",
            "☐ Database integrity verified",
            "☐ API endpoints responding correctly",
            "☐ User-facing features working as expected",
            "☐ Performance metrics acceptable",
            "☐ Security scans passing",
        ]


def create_rollback_planner_agent() -> RollbackPlannerAgent:
    """Factory function to create rollback planner agent."""
    return RollbackPlannerAgent()
