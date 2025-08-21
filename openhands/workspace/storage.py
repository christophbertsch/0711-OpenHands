"""
Storage layer for workspace data
"""

import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

from .models import WorkspaceMetadata, Plan, JobResult


class WorkspaceStorage:
    """File-based storage for workspace data"""
    
    def __init__(self, storage_root: str):
        self.storage_root = Path(storage_root)
        self.storage_root.mkdir(parents=True, exist_ok=True)
    
    def save_workspace_metadata(self, workspace_name: str, metadata: WorkspaceMetadata):
        """Save workspace metadata"""
        workspace_path = self.storage_root / workspace_name
        workspace_path.mkdir(parents=True, exist_ok=True)
        
        metadata_path = workspace_path / "workspace.json"
        metadata_path.write_text(metadata.model_dump_json(indent=2))
    
    def get_workspace_metadata(self, workspace_name: str) -> Optional[WorkspaceMetadata]:
        """Get workspace metadata"""
        metadata_path = self.storage_root / workspace_name / "workspace.json"
        if not metadata_path.exists():
            return None
        
        data = json.loads(metadata_path.read_text())
        return WorkspaceMetadata(**data)
    
    def save_plan(self, workspace_name: str, plan: Plan):
        """Save execution plan"""
        plans_dir = self.storage_root / workspace_name / "context/plans"
        plans_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"{plan.plan_id}.json"
        if plan.status.value == "preview":
            filename = f"{plan.plan_id}.preview.json"
        
        plan_path = plans_dir / filename
        plan_path.write_text(plan.model_dump_json(indent=2))
    
    def get_plan(self, workspace_name: str, plan_id: str) -> Optional[Plan]:
        """Get execution plan"""
        plans_dir = self.storage_root / workspace_name / "context/plans"
        
        # Try both preview and approved versions
        for filename in [f"{plan_id}.json", f"{plan_id}.preview.json"]:
            plan_path = plans_dir / filename
            if plan_path.exists():
                data = json.loads(plan_path.read_text())
                return Plan(**data)
        
        return None
    
    def list_plans(self, workspace_name: str) -> List[Dict[str, Any]]:
        """List all plans for workspace"""
        plans_dir = self.storage_root / workspace_name / "context/plans"
        if not plans_dir.exists():
            return []
        
        plans = []
        for plan_file in plans_dir.glob("*.json"):
            if plan_file.name.endswith(".preview.json"):
                continue  # Skip preview files in listing
            
            try:
                data = json.loads(plan_file.read_text())
                plans.append({
                    "plan_id": data["plan_id"],
                    "status": data["status"],
                    "created_at": data["created_at"],
                    "intent": data["intent_text"][:100] + "..." if len(data["intent_text"]) > 100 else data["intent_text"]
                })
            except Exception:
                continue
        
        return sorted(plans, key=lambda x: x["created_at"], reverse=True)
    
    def save_report(self, workspace_name: str, job_id: str, report_name: str, data: Dict[str, Any]):
        """Save job report"""
        reports_dir = self.storage_root / workspace_name / "context/reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        report_path = reports_dir / f"{job_id}_{report_name}.json"
        report_data = {
            "job_id": job_id,
            "report_name": report_name,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data
        }
        report_path.write_text(json.dumps(report_data, indent=2, default=str))
    
    def get_report(self, workspace_name: str, job_id: str, report_name: str) -> Optional[Dict[str, Any]]:
        """Get job report"""
        report_path = self.storage_root / workspace_name / "context/reports" / f"{job_id}_{report_name}.json"
        if not report_path.exists():
            return None
        
        return json.loads(report_path.read_text())
    
    def list_reports(self, workspace_name: str) -> List[Dict[str, Any]]:
        """List all reports for workspace"""
        reports_dir = self.storage_root / workspace_name / "context/reports"
        if not reports_dir.exists():
            return []
        
        reports = []
        for report_file in reports_dir.glob("*.json"):
            try:
                data = json.loads(report_file.read_text())
                reports.append({
                    "job_id": data["job_id"],
                    "report_name": data["report_name"],
                    "timestamp": data["timestamp"],
                    "file_path": str(report_file)
                })
            except Exception:
                continue
        
        return sorted(reports, key=lambda x: x["timestamp"], reverse=True)
    
    def save_decision(self, workspace_name: str, decision_text: str):
        """Save decision/note to daily log"""
        decisions_dir = self.storage_root / workspace_name / "context/decisions"
        decisions_dir.mkdir(parents=True, exist_ok=True)
        
        today = datetime.utcnow().date()
        decision_file = decisions_dir / f"{today}_notes.md"
        
        timestamp = datetime.utcnow().strftime("%H:%M:%S")
        entry = f"\n\n## {timestamp}\n{decision_text}"
        
        if decision_file.exists():
            content = decision_file.read_text()
            decision_file.write_text(content + entry)
        else:
            decision_file.write_text(f"# Decisions - {today}" + entry)
    
    def save_script(self, workspace_name: str, job_id: str, script_content: str) -> str:
        """Save generated script"""
        scripts_dir = self.storage_root / workspace_name / "scripts"
        scripts_dir.mkdir(parents=True, exist_ok=True)
        
        script_path = scripts_dir / f"{job_id}.py"
        script_path.write_text(script_content)
        
        return str(script_path)
    
    def get_workspace_path(self, workspace_name: str) -> Path:
        """Get workspace directory path"""
        return self.storage_root / workspace_name