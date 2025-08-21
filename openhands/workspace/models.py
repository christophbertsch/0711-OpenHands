"""
Data models for the Workspace system
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class WorkspaceStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    ERROR = "error"


class PlanStatus(str, Enum):
    PREVIEW = "preview"
    APPROVED = "approved"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    ABORTED = "aborted"


class Intent(BaseModel):
    """User's natural language intent for data processing"""
    workspace_name: str
    intent: str
    inputs: List[Dict[str, Any]]
    constraints: Dict[str, Any] = Field(default_factory=dict)
    acceptance: Dict[str, Any] = Field(default_factory=dict)


class PlanOperation(BaseModel):
    """Individual operation in a plan"""
    step: int
    name: str
    description: str
    external_apis: List[str] = Field(default_factory=list)
    outputs: List[str] = Field(default_factory=list)


class Plan(BaseModel):
    """Execution plan generated from user intent"""
    plan_id: str
    workspace_id: str
    status: PlanStatus = PlanStatus.PREVIEW
    inputs: List[Dict[str, Any]]
    operations: List[PlanOperation]
    outputs: List[Dict[str, Any]]
    quotas: Dict[str, Any]
    policies: Dict[str, Any] = Field(default_factory=dict)
    estimates: Dict[str, Any]
    intent_text: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    approved_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class WorkspaceMetadata(BaseModel):
    """Workspace metadata and configuration"""
    workspace_id: str
    project_name: str
    owner: str
    status: WorkspaceStatus = WorkspaceStatus.ACTIVE
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    plans: List[str] = Field(default_factory=list)
    conversations: List[str] = Field(default_factory=list)
    reports: List[str] = Field(default_factory=list)


class JobResult(BaseModel):
    """Result of a workspace job execution"""
    job_id: str
    plan_id: str
    workspace_id: str
    status: str
    outputs: List[Dict[str, Any]]
    logs: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    execution_time: Optional[float] = None
    resource_usage: Dict[str, Any] = Field(default_factory=dict)


class CompetitiveAnalysisResult(BaseModel):
    """Specific result model for competitive analysis tasks"""
    source_products: int
    competitors_found: int
    avg_competitors_per_product: float
    price_analysis: Dict[str, Any]
    market_gaps: List[Dict[str, Any]]
    competitor_landscape: Dict[str, Any]