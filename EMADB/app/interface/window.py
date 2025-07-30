from EMADB.app.variables import EnvironmentVariables
EV = EnvironmentVariables()

from functools import partial
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QAction
from PySide6.QtCore import QFile, QIODevice, Slot, QThreadPool
from PySide6.QtWidgets import (QPushButton, QCheckBox, QPlainTextEdit, 
                               QDoubleSpinBox, QMessageBox, QDialog)

from EMADB.app.utils.driver.toolkit import WebDriverToolkit
from EMADB.app.configuration import Configuration
from EMADB.app.interface.events import SearchEvents
from EMADB.app.interface.dialogs import SaveConfigDialog, LoadConfigDialog
from EMADB.app.interface.workers import Worker
from EMADB.app.logger import logger


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
    
        # set thread pool for the workers
        self.threadpool = QThreadPool.globalInstance()      
        self.worker = None          
     
        # --- Create persistent handlers ---
        self.search_handler = SearchEvents(self.configuration)   
        self.webdriver = WebDriverToolkit(headless=True, ignore_SSL=False)         
        
        # setup UI elements
        self._set_states()
        self.widgets = {}
        self._setup_configuration([
            # actions
            (QAction, 'actionLoadConfig', 'load_configuration_action'),
            (QAction, 'actionSaveConfig', 'save_configuration_action'),
            (QPushButton,'stopSearch','stop_search'),   
            (QCheckBox,"headless",'headless'),
            (QCheckBox,"IgnoreSSL",'ignore_SSL'),
            (QDoubleSpinBox,"waitTime",'wait_time'),
            (QPlainTextEdit,"drugInputs",'text_drug_inputs'),
            (QPushButton,"searchFromFile",'search_file'),
            (QPushButton,"searchFromBox", 'search_box'),
            (QPushButton,"checkDriver", 'check_driver')])
        self._connect_signals([  
            # actions
            ('save_configuration_action', 'triggered', self.save_configuration),   
            ('load_configuration_action', 'triggered', self.load_configuration),                 
            ('stop_search','clicked',self.stop_running_worker),   
            ('search_file','clicked', self.search_from_file),
            ('search_box','clicked', self.search_from_text),
            ('check_driver','clicked', self.check_webdriver)])
        
        self._auto_connect_settings() 

    # [SHOW WINDOW]
    ###########################################################################
    def show(self):        
        self.main_win.show() 

    # [HELPERS]
    ###########################################################################
    def connect_update_setting(self, widget, signal_name, config_key, getter=None):
        if getter is None:
            if isinstance(widget, (QCheckBox)):
                getter = widget.isChecked
            elif isinstance(widget, (QDoubleSpinBox)):
                getter = widget.value            
           
        signal = getattr(widget, signal_name)
        signal.connect(partial(self._update_single_setting, config_key, getter))

    #--------------------------------------------------------------------------
    def _update_single_setting(self, config_key, getter, *args):
        value = getter()
        self.config_manager.update_value(config_key, value)

    #--------------------------------------------------------------------------
    def _auto_connect_settings(self):
        connections = [            
            ('headless', 'toggled', 'headless'),
            ('ignore_SSL', 'toggled', 'ignore_SSL'),
            ('wait_time', 'valueChanged', 'wait_time')]
        
        for attr, signal_name, config_key in connections:
            widget = self.widgets[attr]
            self.connect_update_setting(widget, signal_name, config_key)  

    #--------------------------------------------------------------------------  
    def _set_states(self): 
        pass   

    #--------------------------------------------------------------------------
    def _connect_button(self, button_name: str, slot):        
        button = self.main_win.findChild(QPushButton, button_name)
        button.clicked.connect(slot)     

    #--------------------------------------------------------------------------
    def _start_thread_worker(self, worker : ThreadWorker, on_finished, on_error, on_interrupted):        
        worker.signals.finished.connect(on_finished)
        worker.signals.error.connect(on_error)        
        worker.signals.interrupted.connect(on_interrupted)
        self.threadpool.start(worker)        

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

    #--------------------------------------------------------------------------
    def _set_widgets_from_configuration(self):
        cfg = self.config_manager.get_configuration()
        for attr, widget in self.widgets.items():
            if attr not in cfg:
                continue
            v = cfg[attr]
            # CheckBox
            if hasattr(widget, "setChecked") and isinstance(v, bool):
                widget.setChecked(v)
            # Numeric widgets (SpinBox/DoubleSpinBox)
            elif hasattr(widget, "setValue") and isinstance(v, (int, float)):
                widget.setValue(v)
            # PlainTextEdit/TextEdit
            elif hasattr(widget, "setPlainText") and isinstance(v, str):
                widget.setPlainText(v)
            # LineEdit (or any widget with setText)
            elif hasattr(widget, "setText") and isinstance(v, str):
                widget.setText(v)

    # [SLOT]
    ###########################################################################
    # It's good practice to define methods that act as slots within the class
    # that manages the UI elements. These slots can then call methods on the
    # handler objects. Using @Slot decorator is optional but good practice
    #--------------------------------------------------------------------------
    Slot()
    def stop_running_worker(self):
        if self.worker is not None:
            self.worker.stop()       
        self._send_message("Interrupt requested. Waiting for threads to stop...")

    #--------------------------------------------------------------------------
    # [ACTIONS]
    #--------------------------------------------------------------------------
    @Slot()
    def save_configuration(self):
        dialog = SaveConfigDialog(self.main_win)
        if dialog.exec() == QDialog.Accepted:
            name = dialog.get_name()
            name = 'default_config' if not name else name            
            self.config_manager.save_configuration_to_json(name)
            self._send_message(f"Configuration [{name}] has been saved")

    #--------------------------------------------------------------------------
    @Slot()
    def load_configuration(self):
        dialog = LoadConfigDialog(self.main_win)
        if dialog.exec() == QDialog.Accepted:
            name = dialog.get_selected_config()
            self.config_manager.load_configuration_from_json(name)                
            self._set_widgets_from_configuration()
            self._send_message(f"Loaded configuration [{name}]")

    #--------------------------------------------------------------------------
    @Slot()
    def search_from_file(self):   
        if self.worker:            
            return   
         
        self.configuration = self.config_manager.get_configuration()
        self.search_handler = SearchEvents(self.configuration)           
        # functions that are passed to the worker will be executed in a separate thread
        self.worker = ThreadWorker(self.search_handler.search_using_webdriver)

        # start worker and inject signals
        self._start_thread_worker(
            self.worker, on_finished=self.on_search_finished,
            on_error=self.on_error,
            on_interrupted=self.on_task_interrupted)       

    #--------------------------------------------------------------------------
    @Slot()
    def search_from_text(self):
        if self.worker:            
            return 
                  
        text_box = self.main_win.findChild(QPlainTextEdit, "drugInputs")
        query = text_box.toPlainText()
        drug_list = None if not query else query.strip(',')
        if drug_list is None:
            logger.warning(
                'No drug names in the text box. Proceeding with file screening...')

        self.configuration = self.config_manager.get_configuration()
        self.search_handler = SearchEvents(self.configuration) 

        # functions that are passed to the worker will be executed in a separate thread
        self.worker = ThreadWorker(self.search_handler.search_using_webdriver, drug_list)  

        # start worker and inject signals
        self._start_thread_worker(
            self.worker, on_finished=self.on_search_finished,
            on_error=self.on_error,
            on_interrupted=self.on_task_interrupted)  
       
    #--------------------------------------------------------------------------
    @Slot()
    def check_webdriver(self):         
        if self.webdriver.is_chromedriver_installed():
            version = self.webdriver.check_chrome_version()
            message = f'Chrome driver is installed, current version: {version}'
            QMessageBox.information(
            self.main_win,
            "Chrome driver is installed",
            message,
            QMessageBox.Ok)
        else:
            message = 'Chrome driver is not installed, it will be installed automatically when running search'
            QMessageBox.critical(self.main_win, 'Chrome driver not installed', message)  

    ###########################################################################   
    # [POSITIVE OUTCOME HANDLERS]
    ###########################################################################     
    @Slot(object)
    def on_search_finished(self, search):                       
        message = 'Search for drugs is finished, please check your downloads'   
        self._send_message(message)  
        self.worker = self.worker.cleanup() 
    
    ###########################################################################   
    # [NEGATIVE OUTCOME HANDLERS]
    ###########################################################################     
    @Slot() 
    def on_error(self, err_tb):
        exc, tb = err_tb
        logger.error(f"{exc}\n{tb}")
        message = "An error occurred during the operation. Check the logs for details."
        QMessageBox.critical(self.main_win, 'Something went wrong!', message)             
        self.worker = self.worker.cleanup()  

    ###########################################################################   
    # [INTERRUPTION HANDLERS]
    ###########################################################################
    def on_task_interrupted(self): 
        self._send_message('Current task has been interrupted by user') 
        logger.warning('Current task has been interrupted by user') 
        self.worker = self.worker.cleanup() 
        
          



    