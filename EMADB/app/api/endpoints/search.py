from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from EMADB.app.api.schemas.search import (
    DriverCheckResponse,
    StopTaskRequest,
    TaskResponse,
    TaskStatusResponse,
    TextSearchRequest,
)
from EMADB.app.dependencies import get_search_service
from EMADB.app.utils.services.search_service import SearchService


router = APIRouter(prefix="/search", tags=["search"])


# -----------------------------------------------------------------------------
@router.post("/file", response_model=TaskResponse)
async def search_from_file(
    service: SearchService = Depends(get_search_service),
) -> TaskResponse:
    task = service.start_search_from_file()
    return TaskResponse(task_id=task.task_id, status=task.status.value, message="Search started from file")


# -----------------------------------------------------------------------------
@router.post("/text", response_model=TaskResponse)
async def search_from_text(
    payload: TextSearchRequest,
    service: SearchService = Depends(get_search_service),
) -> TaskResponse:
    task = service.start_search_from_text(payload.query)
    message = "Search started from text box" if payload.query.strip() else "No drug names provided; falling back to file"
    return TaskResponse(task_id=task.task_id, status=task.status.value, message=message)


# -----------------------------------------------------------------------------
@router.post("/stop", response_model=TaskResponse)
async def stop_task(
    payload: StopTaskRequest,
    service: SearchService = Depends(get_search_service),
) -> TaskResponse:
    stopped = service.stop_task(payload.task_id)
    if not stopped:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return TaskResponse(task_id=payload.task_id, status="cancel_requested", message="Interrupt requested")


# -----------------------------------------------------------------------------
@router.get("/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(
    task_id: str,
    service: SearchService = Depends(get_search_service),
) -> TaskStatusResponse:
    snapshot = service.task_status(task_id)
    if snapshot["status"] == "not_found":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return TaskStatusResponse(**snapshot)


# -----------------------------------------------------------------------------
@router.get("/check/driver", response_model=DriverCheckResponse)
async def check_driver(
    service: SearchService = Depends(get_search_service),
) -> DriverCheckResponse:
    result = service.check_driver()
    return DriverCheckResponse(**result)
