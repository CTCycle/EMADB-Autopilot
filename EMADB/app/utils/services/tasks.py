from __future__ import annotations

import threading
import time
import uuid
from concurrent.futures import Future
from enum import Enum
from typing import Any

from EMADB.app.logger import logger


###############################################################################
class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


###############################################################################
class TaskInterrupted(Exception):
    pass


###############################################################################
class SearchTask:
    def __init__(self) -> None:
        self.task_id = str(uuid.uuid4())
        self.future: Future[Any] | None = None
        self.cancel_event = threading.Event()
        self.status = TaskStatus.PENDING
        self.error: str | None = None
        self.result: Any | None = None
        self.started_at: float | None = None
        self.completed_at: float | None = None

    # -------------------------------------------------------------------------
    def set_future(self, future: Future[Any]) -> None:
        self.future = future

    # -------------------------------------------------------------------------
    def mark_running(self) -> None:
        self.status = TaskStatus.RUNNING
        self.started_at = time.time()

    # -------------------------------------------------------------------------
    def mark_completed(self, result: Any | None = None) -> None:
        self.status = TaskStatus.COMPLETED
        self.completed_at = time.time()
        self.result = result

    # -------------------------------------------------------------------------
    def mark_failed(self, error: Exception) -> None:
        self.status = TaskStatus.FAILED
        self.error = str(error)
        self.completed_at = time.time()

    # -------------------------------------------------------------------------
    def mark_cancelled(self) -> None:
        self.status = TaskStatus.CANCELLED
        self.completed_at = time.time()

    # -------------------------------------------------------------------------
    def stop(self) -> None:
        if not self.cancel_event.is_set():
            logger.warning("Current task has been interrupted by user")
            self.cancel_event.set()

    # -------------------------------------------------------------------------
    def is_interrupted(self) -> bool:
        return self.cancel_event.is_set()

    # -------------------------------------------------------------------------
    def snapshot(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "status": self.status.value,
            "error": self.error,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
        }


# -----------------------------------------------------------------------------
def check_thread_status(worker: SearchTask | None) -> None:
    if worker is not None and worker.is_interrupted():
        raise TaskInterrupted()


###############################################################################
class TaskRegistry:
    def __init__(self) -> None:
        self.tasks: dict[str, SearchTask] = {}
        self.lock = threading.Lock()

    # -------------------------------------------------------------------------
    def register(self, task: SearchTask) -> SearchTask:
        with self.lock:
            self.tasks[task.task_id] = task
        return task

    # -------------------------------------------------------------------------
    def get(self, task_id: str) -> SearchTask | None:
        with self.lock:
            return self.tasks.get(task_id)

    # -------------------------------------------------------------------------
    def stop(self, task_id: str) -> bool:
        task = self.get(task_id)
        if task is None:
            return False
        task.stop()
        return True

    # -------------------------------------------------------------------------
    def all_snapshots(self) -> list[dict[str, Any]]:
        with self.lock:
            return [task.snapshot() for task in self.tasks.values()]
