import os
from PySide6.QtCore import QObject, Signal, QRunnable, Slot

from EMADB.commons.constants import ROOT_DIR, DATA_PATH
from EMADB.commons.logger import logger


# [MAIN WINDOW]
###############################################################################
class WorkerSignals(QObject):
    finished = Signal(object)      
    error = Signal(tuple)       


# [MAIN WINDOW]
###############################################################################
class Worker(QRunnable):
    
    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    #--------------------------------------------------------------------------
    @Slot()
    def run(self):
        try:
            result = self.fn(*self.args, **self.kwargs)
            self.signals.finished.emit(None, result)
        except Exception as e:
            self.signals.error.emit(e, None)