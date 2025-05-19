import traceback
import inspect
from PySide6.QtCore import QObject, Signal, QRunnable, Slot

from EMADB.commons.constants import ROOT_DIR, DATA_PATH
from EMADB.commons.logger import logger


###############################################################################
class WorkerSignals(QObject):
    finished = Signal(object)      
    error = Signal(tuple) 
    progress = Signal(int)

    
###############################################################################
class Worker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        # Inspect fn’s signature once, to decide if we should inject:
        sig = inspect.signature(fn)
        params = sig.parameters.values()

        # Accept if it has an explicit 'progress_callback' param
        # or if it has a **kwargs catch‑all
        accepts_progress = any(
            p.name == "progress_callback" or
            p.kind == inspect.Parameter.VAR_KEYWORD
            for p in params)

        # Only inject if it's safe to do so
        if accepts_progress:
            self.kwargs["progress_callback"] = self.signals.progress.emit

    #--------------------------------------------------------------------------
    @Slot()
    def run(self):
        try:
            # If we didn’t inject in __init__, ensure we don’t accidentally pass it
            if "progress_callback" in self.kwargs and \
               "progress_callback" not in inspect.signature(self.fn).parameters:
                self.kwargs.pop("progress_callback")

            result = self.fn(*self.args, **self.kwargs)
            self.signals.finished.emit(result)
        except Exception as e:
            tb = traceback.format_exc()
            self.signals.error.emit((e, tb))