import sys
from PySide6.QtWidgets import QPushButton
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QIODevice, Slot

from EMADB.commons.utils.scraper.driver import WebDriverToolkit
from EMADB.commons.interface.events import SearchEvents
from EMADB.commons.constants import UI_PATH
from EMADB.commons.logger import logger

# [MAIN WINDOW]
###############################################################################
class MainWindow:
    
    def __init__(self, ui_file_path: str): 
        super().__init__()           
        loader = QUiLoader()
        ui_file = QFile(ui_file_path)
        ui_file.open(QIODevice.ReadOnly)
        self.main_win = loader.load(ui_file)
        ui_file.close()  

        # --- Create persistent handlers ---
        # These objects will live as long as the MainWindow instance lives
        self.search_handler = SearchEvents()
        self.webdriver_handler = WebDriverToolkit(headless=False, ignore_SSL=False)

        # --- Connect signals to slots ---
        self._connect_signals()      
   

    #--------------------------------------------------------------------------
    def _connect_button(self, button_name: str, slot):        
        button = self.main_win.findChild(QPushButton, button_name)
        button.clicked.connect(slot)   

    #--------------------------------------------------------------------------
    def _connect_signals(self):        
        self._connect_button("searchFromFile", self.search_from_file_slot)
        self._connect_button("verifyWD", self.verify_webdriver_slot)     

    # --- Slots ---
    # It's good practice to define methods that act as slots within the class
    # that manages the UI elements. These slots can then call methods on the
    # handler objects. Using @Slot decorator is optional but good practice
    #--------------------------------------------------------------------------
    @Slot()
    def search_from_file_slot(self):       
        self.search_handler.search_from_file()

    #--------------------------------------------------------------------------
    @Slot()
    def verify_webdriver_slot(self):        
        is_installed = self.webdriver_handler.is_chromedriver_installed()
        
    #--------------------------------------------------------------------------
    def show(self):        
        self.main_win.show()   

    
