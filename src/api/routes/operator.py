"""
Operator Console & Diagnostic API Router.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import HTMLResponse

from src.api.dependencies import get_agent_state_store
from src.auth import User, require_permission, PERMISSION_OPERATOR_READ
from src.operator.dashboard_service import DashboardService
from src.operator.operator_service import OperatorService
from src.operator.system_service import SystemService
from src.api.responses.standard_response import StandardResponse, success_response
from src.schemas.operator import (
    AuditEventResponse,
    OperatorMemoryResponse,
    OperatorModelResponse,
    OperatorSystemResponse,
    OperatorTaskResponse,
)

router = APIRouter(prefix="/operator", tags=["Operator Console"])


def get_operator_service(
    state_store=Depends(get_agent_state_store),
) -> OperatorService:
    """Dependency provider for OperatorService."""
    return OperatorService(state_store=state_store)


@router.get("/health", response_model=StandardResponse[dict])
async def operator_health(
    user: User = Depends(require_permission(PERMISSION_OPERATOR_READ)),
):
    """Subsystem status diagnostic for Operator Console."""
    return success_response(
        data={"operator_subsystem": "healthy", "user": user.username},
        message="Operator subsystem operational",
    )


@router.get("/system", response_model=StandardResponse[OperatorSystemResponse])
async def get_system_status(
    op_svc: OperatorService = Depends(get_operator_service),
    user: User = Depends(require_permission(PERMISSION_OPERATOR_READ)),
):
    """Retrieve host system platform diagnostic metrics."""
    data = op_svc.system_service.get_system_status()
    resp = OperatorSystemResponse(**data)
    return success_response(data=resp, message="System status retrieved")


@router.get("/models", response_model=StandardResponse[OperatorModelResponse])
async def get_models_overview(
    op_svc: OperatorService = Depends(get_operator_service),
    user: User = Depends(require_permission(PERMISSION_OPERATOR_READ)),
):
    """Retrieve active LLM model catalog and runtime health."""
    data = op_svc.get_models_overview()
    resp = OperatorModelResponse(**data)
    return success_response(data=resp, message="Model catalog status retrieved")


@router.get("/memory", response_model=StandardResponse[OperatorMemoryResponse])
async def get_memory_diagnostics(
    op_svc: OperatorService = Depends(get_operator_service),
    user: User = Depends(require_permission(PERMISSION_OPERATOR_READ)),
):
    """Retrieve RAM and GPU VRAM resource diagnostic metrics."""
    data = op_svc.system_service.get_memory_diagnostics()
    resp = OperatorMemoryResponse(**data)
    return success_response(data=resp, message="Memory diagnostics retrieved")


@router.get("/metrics", response_model=StandardResponse[dict])
async def get_operator_metrics(
    op_svc: OperatorService = Depends(get_operator_service),
    user: User = Depends(require_permission(PERMISSION_OPERATOR_READ)),
):
    """Retrieve raw in-process telemetry metrics map."""
    metrics_map = op_svc.metrics_collector.get_metrics()
    return success_response(data=metrics_map, message="Operator metrics retrieved")


@router.get("/tasks", response_model=StandardResponse[List[OperatorTaskResponse]])
async def get_agent_tasks(
    op_svc: OperatorService = Depends(get_operator_service),
    user: User = Depends(require_permission(PERMISSION_OPERATOR_READ)),
):
    """Retrieve list of active and recent agent task summaries."""
    tasks = op_svc.get_tasks_summary()
    resp = [OperatorTaskResponse(**t) for t in tasks]
    return success_response(data=resp, message="Agent task list retrieved")


@router.get("/audit", response_model=StandardResponse[List[AuditEventResponse]])
async def get_audit_log(
    op_svc: OperatorService = Depends(get_operator_service),
    user: User = Depends(require_permission(PERMISSION_OPERATOR_READ)),
):
    """Retrieve structured audit event log entries."""
    events = op_svc.audit_logger.get_events(limit=50)
    resp = [AuditEventResponse(**e) for e in events]
    return success_response(data=resp, message="Audit log entries retrieved")


@router.get("/dashboard", response_class=HTMLResponse)
async def get_operator_dashboard(
    op_svc: OperatorService = Depends(get_operator_service),
    user: User = Depends(require_permission(PERMISSION_OPERATOR_READ)),
):
    """Render HTML Operator Console dashboard UI."""
    dash_svc = DashboardService(operator_service=op_svc)
    return dash_svc.render_dashboard_html()


@router.get("/recovery", response_model=StandardResponse[dict])
async def get_recovery_status(
    user: User = Depends(require_permission(PERMISSION_OPERATOR_READ)),
):
    """Retrieve startup recovery telemetry and task resilience statistics."""
    from src.agents.recovery import RecoveryManager
    rec_mgr = RecoveryManager()
    stats = rec_mgr.get_recovery_stats()
    return success_response(data=stats, message="Recovery telemetry retrieved")


@router.get("/persistence/status", response_model=StandardResponse[dict])
async def get_persistence_status(
    user: User = Depends(require_permission(PERMISSION_OPERATOR_READ)),
):
    """Retrieve relational database persistence status and table stats."""
    from src.persistence.database import get_db_manager
    from src.persistence.repositories import TaskRepository
    db_mgr = get_db_manager()
    status_info = db_mgr.get_status()

    task_repo = TaskRepository()
    _, total_tasks = task_repo.list_tasks(limit=1)
    status_info["tasks_total"] = total_tasks
    return success_response(data=status_info, message="Persistence status retrieved")


@router.post("/persistence/backup", response_model=StandardResponse[dict])
async def create_persistence_backup(
    user: User = Depends(require_permission(PERMISSION_OPERATOR_READ)),
):
    """Create a local SQLite database snapshot backup."""
    from src.persistence.backup import PersistenceBackupManager
    backup_mgr = PersistenceBackupManager()
    res = backup_mgr.create_database_backup()
    return success_response(data=res, message="Persistence database snapshot backup created")
