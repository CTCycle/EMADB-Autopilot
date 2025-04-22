from PySide6.QtWidgets import QPushButton, QCheckBox, QPlainTextEdit, QSpinBox, QMessageBox
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QIODevice, Slot, QThreadPool

from EMADB.commons.utils.scraper.driver import WebDriverToolkit
from EMADB.commons.interface.configurations import Configurations
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
       
        # initial settings
        self.config_manager = Configurations()
        self.configurations = self.config_manager.get_configurations()

        self.threadpool = QThreadPool.globalInstance()

        # --- Create persistent handlers ---
        # These objects will live as long as the MainWindow instance lives
        self.search_handler = SearchEvents(self.configurations)   
        self.webdriver_handler = WebDriverToolkit(headless=True, ignore_SSL=False)         
        
        # --- modular checkbox setup ---
        self._setup_configurations()

        # --- Connect signals to slots ---
        self._connect_signals()      

    #--------------------------------------------------------------------------
    def _connect_button(self, button_name: str, slot):        
        button = self.main_win.findChild(QPushButton, button_name)
        button.clicked.connect(slot) 

    #--------------------------------------------------------------------------
    def _setup_configurations(self):              
        self.check_headless = self.main_win.findChild(QCheckBox, "Headless")
        self.check_ignore_ssl = self.main_win.findChild(QCheckBox, "IgnoreSSL")
        # set the default value of the wait time box to the current wait time
        self.set_wait_time = self.main_win.findChild(QSpinBox, "waitTime")
        self.set_wait_time.setValue(self.configurations.get('wait_time', 0))
        # connect their toggled signals to our updater
        self.check_headless.toggled.connect(self._update_search_settings)
        self.check_ignore_ssl.toggled.connect(self._update_search_settings) 
        self.set_wait_time.valueChanged.connect(self._update_search_settings)  

    #--------------------------------------------------------------------------
    def _connect_signals(self):        
        self._connect_button("searchFromFile", self.search_from_file)
        self._connect_button("searchFromBox", self.search_from_text)    
        self._connect_button("checkDriver", self.check_webdriver) 

    # --- Slots ---
    # It's good practice to define methods that act as slots within the class
    # that manages the UI elements. These slots can then call methods on the
    # handler objects. Using @Slot decorator is optional but good practice
    #--------------------------------------------------------------------------
    @Slot()
    def _update_search_settings(self):
        self.config_manager.update_value('headless', self.check_headless.isChecked())         
        self.config_manager.update_value('ignore_SSL', self.check_ignore_ssl.isChecked())
        self.config_manager.update_value('wait_time', self.set_wait_time.value())        
            
    #--------------------------------------------------------------------------
    @Slot()
    def search_from_file(self): 
        self.configurations = self.config_manager.get_configurations()
        self.search_handler = SearchEvents(self.configurations)              
        self.threadpool.start(lambda: self.search_handler.search_using_webdriver())       

    #--------------------------------------------------------------------------
    @Slot()
    def search_from_text(self):  
        text_box = self.main_win.findChild(QPlainTextEdit, "drugInputs")
        query = text_box.toPlainText()
        drug_list = None if not query else query.strip(',')

        self.configurations = self.config_manager.get_configurations()
        self.search_handler = SearchEvents(self.configurations)            
        self.threadpool.start(lambda: self.search_handler.search_using_webdriver(drug_list))

    #--------------------------------------------------------------------------
    @Slot()
    def check_webdriver(self):   
        is_installed = self.webdriver_handler.is_chromedriver_installed()
        if is_installed:
            version = self.webdriver_handler.check_chrome_version()
            message = f'Chrome driver is installed, current version: {version}'
            QMessageBox.information(
            self.main_win,
            "Chrome driver is installed",
            message,
            QMessageBox.Ok)
        else:
            message = 'Chrome driver is not installed, it will be installed automatically when running search'
            QMessageBox.critical(self.main_win, 'Chrome driver not installed', message) 

     
    #--------------------------------------------------------------------------
    def show(self):        
        self.main_win.show()   

    
