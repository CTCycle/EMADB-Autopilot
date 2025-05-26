import traceback
import inspect
from PySide6.QtCore import QObject, Signal, QRunnable, Slot

from EMADB.commons.constants import ROOT_DIR, DATA_PATH
from EMADB.commons.logger import logger


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
    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        self._is_interrupted = False 

        sig = inspect.signature(fn)
        params = sig.parameters.values()

        # Accept if it has an explicit 'progress_callback' param or **kwargs
        accepts_progress = any(
            p.name == "progress_callback" or
            p.kind == inspect.Parameter.VAR_KEYWORD
            for p in params)
        
        if accepts_progress:
            self.kwargs["progress_callback"] = self.signals.progress.emit

        # Accept if it has an explicit 'worker' param or **kwargs
        accepts_worker = any(
            p.name == "worker" or
            p.kind == inspect.Parameter.VAR_KEYWORD
            for p in params)
        
        if accepts_worker:
            self.kwargs["worker"] = self 

    #--------------------------------------------------------------------------
    def stop(self):
        self._is_interrupted = True

    #--------------------------------------------------------------------------
    def is_interrupted(self):
        return self._is_interrupted

    #--------------------------------------------------------------------------
    @Slot()    
    def run(self):
        try:
            # Remove progress_callback if not accepted by the function
            if "progress_callback" in self.kwargs and \
               "progress_callback" not in inspect.signature(self.fn).parameters:
                self.kwargs.pop("progress_callback")
            if "worker" in self.kwargs and \
               "worker" not in inspect.signature(self.fn).parameters:
                self.kwargs.pop("worker")
            result = self.fn(*self.args, **self.kwargs)
            self.signals.finished.emit(result)
        except WorkerInterrupted:
            self.signals.interrupted.emit()
        except Exception as e:
            tb = traceback.format_exc()
            self.signals.error.emit((e, tb))


#------------------------------------------------------------------------------
def check_thread_status(worker : Worker):
    if worker is not None and worker.is_interrupted():
        logger.warning('Running thread interrupted by user')
        raise WorkerInterrupted()    

#------------------------------------------------------------------------------
def update_progress_callback(progress, items, progress_callback=None):   
    if progress_callback is not None:
        total = len(items)
        percent = int((progress + 1) * 100 / total)
        progress_callback(percent)   