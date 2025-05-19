from EMADB.commons.variables import EnvironmentVariables
EV = EnvironmentVariables()

from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QIODevice, Slot, QThreadPool
from PySide6.QtWidgets import QPushButton, QCheckBox, QPlainTextEdit, QSpinBox, QMessageBox

from EMADB.commons.variables import EnvironmentVariables
from EMADB.commons.utils.scraper.driver import WebDriverToolkit
from EMADB.commons.configuration import Configuration
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
        self.config_manager = Configuration()
        self.configuration = self.config_manager.get_configuration()
    
        self.threadpool = QThreadPool.globalInstance()      
        self._search_worker = None
     
        # --- Create persistent handlers ---
        # These objects will live as long as the MainWindow instance lives
        self.search_handler = SearchEvents(self.configuration)   
        self.webdriver_handler = WebDriverToolkit(headless=True, ignore_SSL=False)         
        
        # setup UI elements
        self._set_states()
        self.widgets = {}
        self._setup_configuration([
            (QCheckBox,  "Headless", 'check_headless'),
            (QCheckBox,  "IgnoreSSL", 'check_ignore_ssl'),
            (QSpinBox,   "waitTime", 'set_wait_time'),
            (QPlainTextEdit, "drugInputs", 'text_drug_inputs'),
            (QPushButton, "searchFromFile", 'search_file'),
            (QPushButton, "searchFromBox", 'search_box'),
            (QPushButton, "checkDriver", 'check_driver')])
        self._connect_signals([
            ('check_headless',  'toggled', self._update_settings),
            ('check_ignore_ssl','toggled', self._update_settings),
            ('set_wait_time',   'valueChanged', self._update_settings),
            ('search_file', 'clicked', self.search_from_file),
            ('search_box',  'clicked', self.search_from_text),
            ('check_driver','clicked', self.check_webdriver)])

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
    def _setup_configuration(self, widget_defs):
        for cls, name, attr in widget_defs:
            w = self.main_win.findChild(cls, name)
            setattr(self, attr, w)
            self.widgets[attr] = w

    #--------------------------------------------------------------------------
    def _connect_signals(self, connections):
        for attr, signal, slot in connections:
            widget = self.widgets[attr]
            getattr(widget, signal).connect(slot)

    # [SLOT]
    ###########################################################################
    # It's good practice to define methods that act as slots within the class
    # that manages the UI elements. These slots can then call methods on the
    # handler objects. Using @Slot decorator is optional but good practice
    #--------------------------------------------------------------------------
    @Slot()
    def _update_settings(self):
        self.config_manager.update_value('headless', self.check_headless.isChecked())         
        self.config_manager.update_value('ignore_SSL', self.check_ignore_ssl.isChecked())
        self.config_manager.update_value('wait_time', self.set_wait_time.value())        
            
    #--------------------------------------------------------------------------
    @Slot()
    def search_from_file(self): 
        self.main_win.findChild(QPushButton, "searchFromFile").setEnabled(False)
        self.configuration = self.config_manager.get_configuration()
        self.search_handler = SearchEvents(self.configuration)   

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

        self.configuration = self.config_manager.get_configuration()
        self.search_handler = SearchEvents(self.configuration)     

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

    