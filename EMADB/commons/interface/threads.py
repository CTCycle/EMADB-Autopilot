from PySide6.QtCore import QThread, Signal, Slot

from EMADB.commons.utils.scraper.driver import WebDriverToolkit
from EMADB.commons.interface.events import SearchEvents
from EMADB.commons.constants import UI_PATH
from EMADB.commons.logger import logger

# [MAIN WINDOW]
###############################################################################
class SearchThread(QThread):    
    finished = Signal(object)      
    error    = Signal(str)

    def __init__(self, search_handler, drug_list=None):
        super().__init__()
        self.search_handler = search_handler
        self.drug_list = drug_list

    #--------------------------------------------------------------------------
    def run(self):
        try:            
            result = self.search_handler.search_using_webdriver(self.drug_list)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

