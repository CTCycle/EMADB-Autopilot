from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QIODevice, Slot, QThreadPool
from PySide6.QtWidgets import QPushButton, QCheckBox, QPlainTextEdit, QSpinBox, QMessageBox

from EMADB.commons.variables import EnvironmentVariables
from EMADB.commons.utils.scraper.driver import WebDriverToolkit
from EMADB.commons.configurations import Configurations
from EMADB.commons.interface.events import SearchEvents
from EMADB.commons.interface.workers import Worker
from EMADB.commons.constants import UI_PATH
from EMADB.commons.logger import logger


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
        self._search_worker = None        

        # get Hugging Face access token
        EV = EnvironmentVariables()
        self.env_variables = EV.get_environment_variables()

        # --- Create persistent handlers ---
        # These objects will live as long as the MainWindow instance lives
        self.search_handler = SearchEvents(self.configurations)   
        self.webdriver_handler = WebDriverToolkit(headless=True, ignore_SSL=False)         
        
        # setup UI elements
        self._setup_configurations()
        self._connect_signals()
        self._set_states()

    # [SHOW WINDOW]
    ###########################################################################
    def show(self):        
        self.main_win.show()     

    # [HELPERS FOR SETTING CONNECTIONS]
    ###########################################################################
    def _set_states(self): 
        pass   

    #--------------------------------------------------------------------------
    def _connect_button(self, button_name: str, slot):        
        button = self.main_win.findChild(QPushButton, button_name)
        button.clicked.connect(slot)     

    #--------------------------------------------------------------------------
    def _send_message(self, message): 
        self.main_win.statusBar().showMessage(message)

    # [SETUP]
    ###########################################################################
    def _setup_configurations(self):              
        self.check_headless = self.main_win.findChild(QCheckBox, "Headless")
        self.check_ignore_ssl = self.main_win.findChild(QCheckBox, "IgnoreSSL")        
        self.set_wait_time = self.main_win.findChild(QSpinBox, "waitTime")
        
        self.check_headless.toggled.connect(self._update_search_settings)
        self.check_ignore_ssl.toggled.connect(self._update_search_settings) 
        self.set_wait_time.valueChanged.connect(self._update_search_settings)  

    #--------------------------------------------------------------------------
    def _connect_signals(self):        
        self._connect_button("searchFromFile", self.search_from_file)
        self._connect_button("searchFromBox", self.search_from_text)    
        self._connect_button("checkDriver", self.check_webdriver) 

    # [SLOT]
    ###########################################################################
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
        self.main_win.findChild(QPushButton, "searchFromFile").setEnabled(False)
        self.configurations = self.config_manager.get_configurations()
        self.search_handler = SearchEvents(self.configurations)   

        # initialize worker for asynchronous loading of the dataset
        # functions that are passed to the worker will be executed in a separate thread
        self._search_worker = Worker(self.search_handler.search_using_webdriver)
        worker = self._search_worker

        # inject the progress signal into the worker 
        worker.signals.finished.connect(self.on_search_finished)         
        worker.signals.error.connect(self.on_search_error)
        self.threadpool.start(worker)          

    #--------------------------------------------------------------------------
    @Slot()
    def search_from_text(self): 
        self.main_win.findChild(QPushButton, "searchFromBox").setEnabled(False) 

        text_box = self.main_win.findChild(QPlainTextEdit, "drugInputs")
        query = text_box.toPlainText()
        drug_list = None if not query else query.strip(',')
        if drug_list is None:
            logger.warning(
                'No drug names in the text box. Proceeding with file screening...')

        self.configurations = self.config_manager.get_configurations()
        self.search_handler = SearchEvents(self.configurations)     

        # initialize worker for asynchronous loading of the dataset
        # functions that are passed to the worker will be executed in a separate thread
        self._search_worker = Worker(
            self.search_handler.search_using_webdriver, drug_list)
        worker = self._search_worker

        # inject the progress signal into the worker 
        worker.signals.finished.connect(self.on_search_finished)         
        worker.signals.error.connect(self.on_search_error)
        self.threadpool.start(worker)         

    #--------------------------------------------------------------------------
    @Slot()
    def check_webdriver(self):         
        if self.webdriver_handler.is_chromedriver_installed():
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

    # [POSITIVE OUTCOME HANDLERS]
    ###########################################################################     
    @Slot(object)
    def on_search_finished(self, search):                       
        message = 'Search for drugs is finished, please check your downloads'   
        self.search_handler.handle_success(self.main_win, message)
        self.main_win.findChild(QPushButton, "searchFromFile").setEnabled(True)   
        self.main_win.findChild(QPushButton, "searchFromBox").setEnabled(True) 
    
    # [NEGATIVE OUTCOME HANDLERS]
    ###########################################################################    
    @Slot(tuple)
    def on_search_error(self, err_tb):
        self.search_handler.handle_error(self.main_win, err_tb)
        self.main_win.findChild(QPushButton, "searchFromFile").setEnabled(True)   
        self.main_win.findChild(QPushButton, "searchFromBox").setEnabled(True)   

    