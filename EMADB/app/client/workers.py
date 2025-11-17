from __future__ import annotations

import inspect
import traceback
from collections.abc import Callable
from typing import Any

from PySide6.QtCore import QObject, QRunnable, Signal, Slot

from EMADB.app.utils.logger import logger


###############################################################################
class WorkerInterrupted(Exception):
    """Exception to indicate worker was intentionally interrupted."""

    pass


###############################################################################
class WorkerSignals(QObject):
    finished = Signal(object)
    error = Signal(tuple)
    interrupted = Signal()
    progress = Signal(int)


###############################################################################
class Worker(QRunnable):
    def __init__(self, fn: Callable[[], None], *args: Any, **kwargs: Any) -> None:
        """
        Prepare a QRunnable with cooperative interruption and progress hooks.

        Keyword arguments:
            fn: Callable executed on the worker thread.
            args: Positional arguments forwarded to the callable.
            kwargs: Keyword arguments forwarded to the callable.
        Return value:
            None
        """
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        self.interruption_state = False

        sig = inspect.signature(fn)
        params = sig.parameters.values()

        # Accept if it has an explicit 'progress_callback' param or **kwargs
        accepts_progress = any(
            p.name == "progress_callback" or p.kind == inspect.Parameter.VAR_KEYWORD
            for p in params
        )

        if accepts_progress:
            self.kwargs["progress_callback"] = self.signals.progress.emit

        # Accept if it has an explicit 'worker' param or **kwargs
        accepts_worker = any(
            p.name == "worker" or p.kind == inspect.Parameter.VAR_KEYWORD
            for p in params
        )

        if accepts_worker:
            self.kwargs["worker"] = self

    # -------------------------------------------------------------------------
    def stop(self) -> None:
        self.interruption_state = True

    # -------------------------------------------------------------------------
    def is_interrupted(self) -> bool:
        return self.interruption_state

    # -------------------------------------------------------------------------
    @Slot()
    def run(self) -> None:
        """
        Execute the target callable and emit lifecycle signals accordingly.

        Keyword arguments:
            None
        Return value:
            None
        """
        try:
            # Remove progress_callback if not accepted by the function
            if (
                "progress_callback" in self.kwargs
                and "progress_callback" not in inspect.signature(self.fn).parameters
            ):
                self.kwargs.pop("progress_callback")
            if (
                "worker" in self.kwargs
                and "worker" not in inspect.signature(self.fn).parameters
            ):
                self.kwargs.pop("worker")
            result = self.fn(*self.args, **self.kwargs)
            self.signals.finished.emit(result)
        except WorkerInterrupted:
            self.signals.interrupted.emit()
        except Exception as e:
            tb = traceback.format_exc()
            self.signals.error.emit((e, tb))

    # -------------------------------------------------------------------------
    def cleanup(self) -> None:
        pass


# -----------------------------------------------------------------------------
def check_thread_status(worker: Worker | None) -> None:
    if worker is not None and worker.is_interrupted():
        logger.warning("Running thread interrupted by user")
        raise WorkerInterrupted()
