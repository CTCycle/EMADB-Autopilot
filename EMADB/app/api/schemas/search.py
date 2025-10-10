from __future__ import annotations

from pydantic import BaseModel


###############################################################################
class TextSearchRequest(BaseModel):
    query: str


###############################################################################
class StopTaskRequest(BaseModel):
    task_id: str


###############################################################################
class TaskResponse(BaseModel):
    task_id: str
    status: str
    message: str | None = None


###############################################################################
class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    error: str | None = None
    started_at: float | None = None
    completed_at: float | None = None


###############################################################################
class DriverCheckResponse(BaseModel):
    status: str
    message: str
