import gc
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
class ThreadWorker(QRunnable):
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
            # Remove progress_callback and worker if not accepted by the function
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

    #--------------------------------------------------------------------------
    @Slot()
    def cleanup(self):
        """
        Disconnects all signals and cleans up resources.
        Call this from the main thread after the worker has completed.
        """        
        try:
            # Disconnect all signals explicitly to prevent dangling connections
            if self.signals:
                self.signals.finished.disconnect()
                self.signals.error.disconnect()
                self.signals.interrupted.disconnect()
                self.signals.progress.disconnect()
            
            # 3. Break potential reference cycles for faster garbage collection
            self.fn = None
            self.args = None
            self.kwargs = None
            self.signals = None
            
            # 4. Force garbage collection
            gc.collect()           
            
        except Exception as e:
            logger.error(f"Error during worker cleanup: {e}")


#------------------------------------------------------------------------------
def check_thread_status(worker : ThreadWorker):
    if worker is not None and worker.is_interrupted():        
        raise WorkerInterrupted()    

#------------------------------------------------------------------------------
def update_progress_callback(progress, total, progress_callback=None):   
    if progress_callback is not None:        
        percent = int((progress + 1) * 100 / total)
        progress_callback(percent)  