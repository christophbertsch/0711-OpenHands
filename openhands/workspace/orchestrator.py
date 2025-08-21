"""
Workspace Orchestrator - Main coordination service
"""

import json
import uuid
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

from .models import Intent, Plan, WorkspaceMetadata, PlanStatus, PlanOperation
from .agents import WorkspaceAgentPipeline
from .storage import WorkspaceStorage
from ..events import EventStream


class WorkspaceOrchestrator:
    """Main orchestrator for workspace operations"""
    
    def __init__(self, storage_root: str = "/tmp/workspaces", event_stream: Optional[EventStream] = None):
        self.storage_root = Path(storage_root)
        self.storage = WorkspaceStorage(storage_root)
        self.agent_pipeline = WorkspaceAgentPipeline()
        self.agent_pipeline.storage = self.storage  # Set storage reference
        self.event_stream = event_stream
        
    def create_workspace(self, name: str, owner: str) -> WorkspaceMetadata:
        """Create a new workspace"""
        workspace_id = f"ws_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:6]}"
        
        metadata = WorkspaceMetadata(
            workspace_id=workspace_id,
            project_name=name,
            owner=owner
        )
        
        # Initialize workspace directory structure
        workspace_path = self.storage_root / name
        self._init_workspace_structure(workspace_path, metadata)
        
        # Store metadata
        self.storage.save_workspace_metadata(name, metadata)
        
        # Event stream integration would go here in production
        # if self.event_stream:
        #     self.event_stream.add_event(WorkspaceCreatedEvent(...))
        
        return metadata
    
    def submit_intent(self, workspace_name: str, intent: Intent) -> Plan:
        """Process user intent and generate plan preview"""
        workspace_metadata = self.storage.get_workspace_metadata(workspace_name)
        if not workspace_metadata:
            raise ValueError(f"Workspace {workspace_name} not found")
        
        # Generate plan using agent pipeline
        plan = self.agent_pipeline.generate_plan(intent, workspace_metadata.workspace_id)
        
        # Store plan preview
        self.storage.save_plan(workspace_name, plan)
        
        # Event stream integration would go here in production
        # if self.event_stream:
        #     self.event_stream.add_event(PlanCreatedEvent(...))
        
        return plan
    
    def approve_plan(self, workspace_name: str, plan_id: str) -> str:
        """Approve a plan and start execution"""
        plan = self.storage.get_plan(workspace_name, plan_id)
        if not plan:
            raise ValueError(f"Plan {plan_id} not found")
        
        if plan.status != PlanStatus.PREVIEW:
            raise ValueError(f"Plan {plan_id} is not in preview status")
        
        # Update plan status
        plan.status = PlanStatus.APPROVED
        plan.approved_at = datetime.utcnow()
        self.storage.save_plan(workspace_name, plan)
        
        # Generate job ID and start execution
        job_id = f"job_{uuid.uuid4().hex[:8]}"
        
        # Event stream integration would go here in production
        # if self.event_stream:
        #     self.event_stream.add_event(PlanApprovedEvent(...))
        
        # Start agent pipeline execution
        # For demo, execute synchronously. In production, this would be async/background
        self.agent_pipeline.execute_plan(workspace_name, job_id, plan)
        
        # Update plan in storage after execution
        self.storage.save_plan(workspace_name, plan)
        
        return job_id
    
    def get_workspace_status(self, workspace_name: str) -> Dict:
        """Get current workspace status and activity"""
        metadata = self.storage.get_workspace_metadata(workspace_name)
        if not metadata:
            raise ValueError(f"Workspace {workspace_name} not found")
        
        # Get recent plans
        plans = self.storage.list_plans(workspace_name)
        
        # Get recent jobs/reports
        reports = self.storage.list_reports(workspace_name)
        
        return {
            "metadata": metadata,
            "recent_plans": plans[-5:],  # Last 5 plans
            "recent_reports": reports[-10:],  # Last 10 reports
            "workspace_path": str(self.storage_root / workspace_name)
        }
    
    def _init_workspace_structure(self, workspace_path: Path, metadata: WorkspaceMetadata):
        """Initialize workspace directory structure"""
        dirs = [
            "data/uploads", "data/outputs", "data/intermediate",
            "scripts/helpers", "context/plans", "context/decisions", 
            "context/reports", "context/conversations", "context/data_profiles",
            "context/prompts", "context/embeddings", "docs", ".vscode"
        ]
        
        for dir_path in dirs:
            (workspace_path / dir_path).mkdir(parents=True, exist_ok=True)
        
        # Create README
        readme_content = f"""# {metadata.project_name}

This workspace is managed by OpenHands Workspace system.
All compute operations are handled by microagents in sandboxed environments.

**Workspace ID:** {metadata.workspace_id}
**Owner:** {metadata.owner}
**Created:** {metadata.created_at.isoformat()}

## Structure
- `data/` - Input files, outputs, and intermediate processing files
- `scripts/` - Generated Python scripts and helpers
- `context/` - Plans, decisions, reports, and conversation history
- `docs/` - Documentation and analysis reports

## Usage
Do not run scripts locally. All execution happens through the OpenHands Workspace system.
"""
        (workspace_path / "docs/README.md").write_text(readme_content)
        
        # Create VS Code settings
        vscode_settings = {
            "python.defaultInterpreterPath": "python",
            "editor.formatOnSave": True,
            "files.exclude": {"**/__pycache__": True, "**/.git": True},
            "python.analysis.disabled": ["too-many-arguments", "unused-import"]
        }
        (workspace_path / ".vscode/settings.json").write_text(json.dumps(vscode_settings, indent=2))
        
        # Create extensions recommendations
        vscode_extensions = {
            "recommendations": [
                "ms-python.python",
                "ms-python.vscode-pylance", 
                "yzhang.markdown-all-in-one",
                "ms-vscode.vscode-json"
            ]
        }
        (workspace_path / ".vscode/extensions.json").write_text(json.dumps(vscode_extensions, indent=2))
        
        # Create workspace manifest
        manifest = {
            "workspace_id": metadata.workspace_id,
            "plans": [],
            "conversations": [],
            "decisions": [],
            "reports": [],
            "embeddings": {
                "driver": "sqlite",
                "path": "context/embeddings/index.sqlite"
            }
        }
        (workspace_path / "context/manifest.json").write_text(json.dumps(manifest, indent=2))
        
        # Create workspace.json
        (workspace_path / "workspace.json").write_text(metadata.model_dump_json(indent=2))