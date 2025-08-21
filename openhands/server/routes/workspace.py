"""
Workspace API routes for OpenHands
"""

import os
import shutil
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

from ...workspace import Intent, WorkspaceOrchestrator

# from ..dependencies import get_current_user  # TODO: Implement proper auth


def get_current_user():
    """Mock current user for demo - replace with real auth"""
    return 'demo_user'


router = APIRouter(prefix='/api/workspaces', tags=['workspace'])

# Initialize orchestrator
WORKSPACES_ROOT = os.environ.get('WORKSPACES_ROOT', '/tmp/openhands_workspaces')
orchestrator = WorkspaceOrchestrator(storage_root=WORKSPACES_ROOT)


@router.post('')
async def create_workspace(
    name: str = Form(...),
    owner: str = Form(...),
    current_user: Optional[str] = Depends(get_current_user),
):
    """Create a new workspace"""
    try:
        # Use current user if available, otherwise use provided owner
        workspace_owner = current_user or owner

        metadata = orchestrator.create_workspace(name, workspace_owner)

        return {
            'success': True,
            'workspace': metadata.model_dump(),
            'path': str(Path(WORKSPACES_ROOT) / name),
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post('/{workspace_name}/upload')
async def upload_file(
    workspace_name: str,
    file: UploadFile,
    current_user: Optional[str] = Depends(get_current_user),
):
    """Upload a file to workspace"""
    try:
        workspace_path = Path(WORKSPACES_ROOT) / workspace_name
        if not workspace_path.exists():
            raise HTTPException(status_code=404, detail='Workspace not found')

        # Create uploads directory
        uploads_dir = workspace_path / 'data' / 'uploads'
        uploads_dir.mkdir(parents=True, exist_ok=True)

        # Save uploaded file
        file_path = uploads_dir / file.filename
        with file_path.open('wb') as buffer:
            shutil.copyfileobj(file.file, buffer)

        return {
            'success': True,
            'file_path': f'data/uploads/{file.filename}',
            'file_size': file_path.stat().st_size,
            'content_type': file.content_type,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post('/{workspace_name}/intents')
async def submit_intent(
    workspace_name: str,
    intent: Intent,
    current_user: Optional[str] = Depends(get_current_user),
):
    """Submit user intent and get plan preview"""
    try:
        plan = orchestrator.submit_intent(workspace_name, intent)

        return {
            'success': True,
            'plan_preview': plan.model_dump(),
            'requires_approval': True,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post('/{workspace_name}/approve')
async def approve_plan(
    workspace_name: str,
    plan_id: str = Form(...),
    current_user: Optional[str] = Depends(get_current_user),
):
    """Approve a plan and start execution"""
    try:
        job_id = orchestrator.approve_plan(workspace_name, plan_id)

        return {
            'success': True,
            'job_id': job_id,
            'status': 'queued',
            'message': 'Plan approved and execution started',
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get('/{workspace_name}/status')
async def get_workspace_status(
    workspace_name: str, current_user: Optional[str] = Depends(get_current_user)
):
    """Get workspace status and recent activity"""
    try:
        status = orchestrator.get_workspace_status(workspace_name)

        return {'success': True, **status}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get('/{workspace_name}/plans')
async def list_plans(
    workspace_name: str, current_user: Optional[str] = Depends(get_current_user)
):
    """List all plans for workspace"""
    try:
        plans = orchestrator.storage.list_plans(workspace_name)

        return {'success': True, 'plans': plans}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get('/{workspace_name}/plans/{plan_id}')
async def get_plan(
    workspace_name: str,
    plan_id: str,
    current_user: Optional[str] = Depends(get_current_user),
):
    """Get specific plan details"""
    try:
        plan = orchestrator.storage.get_plan(workspace_name, plan_id)
        if not plan:
            raise HTTPException(status_code=404, detail='Plan not found')

        return {'success': True, 'plan': plan.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get('/{workspace_name}/reports')
async def list_reports(
    workspace_name: str, current_user: Optional[str] = Depends(get_current_user)
):
    """List all reports for workspace"""
    try:
        reports = orchestrator.storage.list_reports(workspace_name)

        return {'success': True, 'reports': reports}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get('/{workspace_name}/reports/{job_id}/{report_name}')
async def get_report(
    workspace_name: str,
    job_id: str,
    report_name: str,
    current_user: Optional[str] = Depends(get_current_user),
):
    """Get specific report"""
    try:
        report = orchestrator.storage.get_report(workspace_name, job_id, report_name)
        if not report:
            raise HTTPException(status_code=404, detail='Report not found')

        return {'success': True, 'report': report}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get('/{workspace_name}/outputs/{file_path:path}')
async def download_output(
    workspace_name: str,
    file_path: str,
    current_user: Optional[str] = Depends(get_current_user),
):
    """Download workspace output file"""
    try:
        workspace_path = Path(WORKSPACES_ROOT) / workspace_name
        full_file_path = workspace_path / file_path

        # Security check - ensure file is within workspace
        if not str(full_file_path.resolve()).startswith(str(workspace_path.resolve())):
            raise HTTPException(status_code=403, detail='Access denied')

        if not full_file_path.exists():
            raise HTTPException(status_code=404, detail='File not found')

        return FileResponse(
            path=str(full_file_path),
            filename=full_file_path.name,
            media_type='application/octet-stream',
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete('/{workspace_name}')
async def delete_workspace(
    workspace_name: str, current_user: Optional[str] = Depends(get_current_user)
):
    """Delete workspace (admin only)"""
    try:
        workspace_path = Path(WORKSPACES_ROOT) / workspace_name
        if workspace_path.exists():
            shutil.rmtree(workspace_path)

        return {'success': True, 'message': f'Workspace {workspace_name} deleted'}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get('')
async def list_workspaces(current_user: Optional[str] = Depends(get_current_user)):
    """List all workspaces"""
    try:
        workspaces_root = Path(WORKSPACES_ROOT)
        workspaces = []

        if workspaces_root.exists():
            for workspace_dir in workspaces_root.iterdir():
                if workspace_dir.is_dir():
                    workspace_json = workspace_dir / 'workspace.json'
                    if workspace_json.exists():
                        try:
                            import json

                            metadata = json.loads(workspace_json.read_text())
                            workspaces.append(
                                {
                                    'name': workspace_dir.name,
                                    'workspace_id': metadata.get('workspace_id'),
                                    'owner': metadata.get('owner'),
                                    'created_at': metadata.get('created_at'),
                                    'status': metadata.get('status', 'active'),
                                }
                            )
                        except Exception:
                            continue

        return {'success': True, 'workspaces': workspaces}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
