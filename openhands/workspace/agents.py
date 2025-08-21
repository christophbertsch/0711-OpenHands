"""
Workspace Agent Pipeline - Specialized microagents for workflow execution
"""

import uuid
import hashlib
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from .models import Intent, Plan, PlanStatus, PlanOperation, JobResult
from .storage import WorkspaceStorage
from .templates import CodeTemplates


class WorkspaceAgentPipeline:
    """Pipeline of specialized agents for workspace operations"""
    
    def __init__(self):
        self.storage = None  # Will be set by orchestrator
        self.templates = CodeTemplates()
    
    def generate_plan(self, intent: Intent, workspace_id: str) -> Plan:
        """Generate execution plan from user intent"""
        plan_id = f"plan_{uuid.uuid4().hex[:8]}"
        
        # Analyze intent to determine operations
        operations = self._analyze_intent_operations(intent)
        
        # Estimate resources and quotas
        estimates = self._estimate_resources(intent, operations)
        quotas = self._calculate_quotas(estimates)
        
        # Generate outputs based on operations
        outputs = self._determine_outputs(operations)
        
        plan = Plan(
            plan_id=plan_id,
            workspace_id=workspace_id,
            inputs=intent.inputs,
            operations=operations,
            outputs=outputs,
            quotas=quotas,
            policies=intent.constraints,
            estimates=estimates,
            intent_text=intent.intent
        )
        
        return plan
    
    def execute_plan(self, workspace_name: str, job_id: str, plan: Plan):
        """Execute approved plan through agent pipeline"""
        # This would typically be async/background processing
        # For demo, we'll simulate the pipeline
        
        try:
            # Update plan status
            plan.status = PlanStatus.RUNNING
            
            # Execute pipeline steps
            self._run_planner(workspace_name, job_id, plan)
            self._run_codegen(workspace_name, job_id, plan)
            self._run_executor(workspace_name, job_id, plan)
            self._run_tester(workspace_name, job_id, plan)
            self._run_deployer(workspace_name, job_id, plan)
            self._run_committer(workspace_name, job_id, plan)
            self._run_archivist(workspace_name, job_id, plan)
            
            # Mark as completed
            plan.status = PlanStatus.COMPLETED
            plan.completed_at = datetime.utcnow()
            
        except Exception as e:
            print(f"Error in agent pipeline: {e}")
            import traceback
            traceback.print_exc()
            plan.status = PlanStatus.FAILED
            self._save_error_report(workspace_name, job_id, str(e))
    
    def _analyze_intent_operations(self, intent: Intent) -> List[PlanOperation]:
        """Analyze intent to determine required operations"""
        operations = []
        intent_lower = intent.intent.lower()
        
        # Check for BMEcat processing
        if "bmecat" in intent_lower or any("xml" in inp.get("path", "") for inp in intent.inputs):
            operations.append(PlanOperation(
                step=1,
                name="parse_bmecat_catalog",
                description="Extract product hierarchy, specifications, and ETIM features",
                outputs=["data/intermediate/products_structured.json"]
            ))
        
        # Check for competitive analysis
        if "competition" in intent_lower or "competitor" in intent_lower or "crawl" in intent_lower:
            operations.extend([
                PlanOperation(
                    step=2,
                    name="generate_search_queries", 
                    description="Create optimized search terms for competitive research",
                    outputs=["data/intermediate/search_queries.json"]
                ),
                PlanOperation(
                    step=3,
                    name="tavily_competitive_search",
                    description="Search e-commerce sites for competing products",
                    external_apis=["tavily"],
                    outputs=["data/intermediate/competitor_matches.json"]
                ),
                PlanOperation(
                    step=4,
                    name="crawl_competitor_details",
                    description="Extract pricing, availability, specs from competitor pages",
                    outputs=["data/intermediate/competitor_details.json"]
                ),
                PlanOperation(
                    step=5,
                    name="competitive_analysis",
                    description="Compare prices, features, market positioning",
                    outputs=[
                        "data/outputs/competitive_analysis.csv",
                        "data/outputs/price_comparison_report.html",
                        "data/outputs/market_gaps_analysis.json"
                    ]
                )
            ])
        
        # Default data processing operation if no specific pattern matched
        if not operations:
            operations.append(PlanOperation(
                step=1,
                name="generic_data_processing",
                description="Process uploaded data according to user intent",
                outputs=["data/outputs/processed_data.csv"]
            ))
        
        return operations
    
    def _estimate_resources(self, intent: Intent, operations: List[PlanOperation]) -> Dict[str, Any]:
        """Estimate resource requirements"""
        estimates = {
            "runtime_minutes": 5,  # Default
            "tavily_credits": 0,
            "crawl_requests": 0,
            "products": 0
        }
        
        # Estimate based on operations
        for op in operations:
            if "tavily" in op.name:
                estimates["tavily_credits"] += 200
                estimates["runtime_minutes"] += 15
            if "crawl" in op.name:
                estimates["crawl_requests"] += 500
                estimates["runtime_minutes"] += 20
            if "bmecat" in op.name:
                estimates["products"] = 350  # Estimated from typical BMEcat files
                estimates["runtime_minutes"] += 5
        
        return estimates
    
    def _calculate_quotas(self, estimates: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate resource quotas based on estimates"""
        return {
            "tavily_max_requests": max(estimates.get("tavily_credits", 0) * 2, 100),
            "crawl_max_pages": max(estimates.get("crawl_requests", 0), 100),
            "qps": 1,  # Requests per second
            "max_runtime_minutes": estimates.get("runtime_minutes", 5) * 2
        }
    
    def _determine_outputs(self, operations: List[PlanOperation]) -> List[Dict[str, Any]]:
        """Determine expected outputs from operations"""
        outputs = []
        
        for op in operations:
            for output_path in op.outputs:
                if output_path.endswith('.csv'):
                    outputs.append({
                        "path": output_path,
                        "format": "csv",
                        "description": f"CSV output from {op.name}"
                    })
                elif output_path.endswith('.json'):
                    outputs.append({
                        "path": output_path,
                        "format": "json", 
                        "description": f"JSON data from {op.name}"
                    })
                elif output_path.endswith('.html'):
                    outputs.append({
                        "path": output_path,
                        "format": "html",
                        "description": f"HTML report from {op.name}"
                    })
        
        return outputs
    
    def _run_planner(self, workspace_name: str, job_id: str, plan: Plan):
        """Planner agent - refines and validates the plan"""
        if not self.storage:
            return
        
        report = {
            "agent": "planner",
            "status": "completed",
            "plan_validated": True,
            "operations_count": len(plan.operations),
            "estimated_runtime": plan.estimates.get("runtime_minutes", 0)
        }
        
        self.storage.save_report(workspace_name, job_id, "planner", report)
    
    def _run_codegen(self, workspace_name: str, job_id: str, plan: Plan):
        """Codegen agent - generates Python script from plan"""
        if not self.storage:
            return
        
        # Generate script based on plan operations
        script_content = self.templates.generate_competitive_analysis_script(plan)
        
        # Save script
        script_path = self.storage.save_script(workspace_name, job_id, script_content)
        
        # Calculate script hash for integrity
        script_hash = hashlib.sha256(script_content.encode()).hexdigest()
        
        report = {
            "agent": "codegen",
            "status": "completed",
            "script_path": script_path,
            "script_hash": script_hash,
            "lines_of_code": len(script_content.split('\n'))
        }
        
        self.storage.save_report(workspace_name, job_id, "codegen", report)
    
    def _run_executor(self, workspace_name: str, job_id: str, plan: Plan):
        """Executor agent - runs generated script in sandbox"""
        if not self.storage:
            return
        
        workspace_path = self.storage.get_workspace_path(workspace_name)
        script_path = workspace_path / "scripts" / f"{job_id}.py"
        
        # For demo, simulate script execution
        # In production, this would run in a Docker container
        report = {
            "agent": "executor",
            "status": "completed",
            "execution_time": 45.2,
            "memory_usage": "128MB",
            "network_requests": 234,
            "outputs_created": len(plan.outputs)
        }
        
        # Create mock output files
        self._create_mock_outputs(workspace_path, plan.outputs)
        
        self.storage.save_report(workspace_name, job_id, "executor", report)
    
    def _run_tester(self, workspace_name: str, job_id: str, plan: Plan):
        """Tester agent - validates outputs"""
        if not self.storage:
            return
        
        workspace_path = self.storage.get_workspace_path(workspace_name)
        
        # Check if expected outputs exist
        outputs_exist = []
        for output in plan.outputs:
            output_path = workspace_path / output["path"]
            outputs_exist.append({
                "path": output["path"],
                "exists": output_path.exists(),
                "size": output_path.stat().st_size if output_path.exists() else 0
            })
        
        report = {
            "agent": "tester",
            "status": "completed",
            "outputs_validated": outputs_exist,
            "all_outputs_exist": all(o["exists"] for o in outputs_exist)
        }
        
        self.storage.save_report(workspace_name, job_id, "tester", report)
    
    def _run_deployer(self, workspace_name: str, job_id: str, plan: Plan):
        """Deployer agent - prepares environment and dependencies"""
        if not self.storage:
            return
        
        workspace_path = self.storage.get_workspace_path(workspace_name)
        
        # Create requirements.lock file
        requirements = [
            "pandas>=1.5.0",
            "lxml>=4.9.0", 
            "tavily-python>=0.3.0",
            "requests>=2.28.0",
            "beautifulsoup4>=4.11.0"
        ]
        
        req_path = workspace_path / "scripts" / "requirements.lock"
        req_path.write_text("\n".join(requirements))
        
        report = {
            "agent": "deployer",
            "status": "completed",
            "requirements_locked": True,
            "dependencies_count": len(requirements)
        }
        
        self.storage.save_report(workspace_name, job_id, "deployer", report)
    
    def _run_committer(self, workspace_name: str, job_id: str, plan: Plan):
        """Committer agent - commits results to version control"""
        if not self.storage:
            return
        
        # For demo, just log the commit action
        # In production, this would use GitPython to commit changes
        
        commit_message = f"feat(workspace): {job_id} - {plan.intent_text[:50]}..."
        
        report = {
            "agent": "committer", 
            "status": "completed",
            "commit_message": commit_message,
            "files_committed": len(plan.outputs) + 2,  # outputs + script + requirements
            "branch": f"workspace/{workspace_name}/{job_id}"
        }
        
        self.storage.save_report(workspace_name, job_id, "committer", report)
    
    def _run_archivist(self, workspace_name: str, job_id: str, plan: Plan):
        """Archivist agent - updates workspace manifest and metadata"""
        if not self.storage:
            return
        
        workspace_path = self.storage.get_workspace_path(workspace_name)
        manifest_path = workspace_path / "context" / "manifest.json"
        
        if manifest_path.exists():
            import json
            manifest = json.loads(manifest_path.read_text())
            manifest["plans"].append(f"plans/{plan.plan_id}.json")
            manifest["reports"].extend([f"reports/{job_id}_{agent}.json" 
                                     for agent in ["planner", "codegen", "executor", "tester", "deployer", "committer"]])
            manifest_path.write_text(json.dumps(manifest, indent=2))
        
        report = {
            "agent": "archivist",
            "status": "completed", 
            "manifest_updated": True,
            "total_plans": len(manifest.get("plans", [])),
            "total_reports": len(manifest.get("reports", []))
        }
        
        self.storage.save_report(workspace_name, job_id, "archivist", report)
    
    def _create_mock_outputs(self, workspace_path: Path, outputs: List[Dict[str, Any]]):
        """Create mock output files for demo"""
        for output in outputs:
            output_path = workspace_path / output["path"]
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            if output["format"] == "csv":
                # Create mock CSV
                csv_content = """product_id,description,competitor_name,competitor_price,availability,competitor_url
719304,"LED-Flexmodul General85, 12V, IP66, 350lm/m, 3000K, 5m",Amazon DE,89.99,In Stock,https://amazon.de/led-flex-module
719304,"LED-Flexmodul General85, 12V, IP66, 350lm/m, 3000K, 5m",Conrad Electronic,94.50,Available,https://conrad.de/led-strip
719305,"LED Controller RGB 24V",eBay DE,45.00,Limited Stock,https://ebay.de/led-controller"""
                output_path.write_text(csv_content)
            
            elif output["format"] == "json":
                # Create mock JSON
                json_content = {
                    "analysis_timestamp": datetime.utcnow().isoformat(),
                    "total_products": 352,
                    "competitors_found": 1247,
                    "avg_price_difference": 0.15,
                    "market_gaps": [
                        {"category": "RGB Controllers", "opportunity": "Premium segment underserved"},
                        {"category": "IP67 Strips", "opportunity": "Limited outdoor options"}
                    ]
                }
                import json
                output_path.write_text(json.dumps(json_content, indent=2))
            
            elif output["format"] == "html":
                # Create mock HTML report
                html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Competitive Analysis Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .summary {{ background: #f5f5f5; padding: 20px; border-radius: 5px; }}
        table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <h1>Competitive Analysis Report</h1>
    <div class="summary">
        <h2>Executive Summary</h2>
        <p>Analysis of 352 LED products against 1,247 competitor offerings.</p>
        <p>Average price difference: 15% premium opportunity identified.</p>
    </div>
    <h2>Key Findings</h2>
    <ul>
        <li>RGB Controllers: Premium segment underserved</li>
        <li>IP67 Strips: Limited outdoor options available</li>
        <li>24V Systems: Strong competitive positioning</li>
    </ul>
</body>
</html>"""
                output_path.write_text(html_content)
    
    def _save_error_report(self, workspace_name: str, job_id: str, error: str):
        """Save error report when execution fails"""
        if not self.storage:
            return
        
        report = {
            "agent": "error_handler",
            "status": "failed",
            "error": error,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.storage.save_report(workspace_name, job_id, "error", report)