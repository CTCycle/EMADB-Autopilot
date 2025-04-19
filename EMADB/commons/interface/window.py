import sys
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QPushButton,
                               QTextEdit, QStatusBar, QMessageBox)
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QIODevice, Slot, QCoreApplication

from EMADB.commons.utils.scraper.driver import WebDriverToolkit
from EMADB.commons.interface.events import SearchEvents
from EMADB.commons.interface.workers import MenuActions
from EMADB.commons.constants import UI_PATH
from EMADB.commons.logger import logger

# [MAIN WINDOW]
###############################################################################
class MainWindow:
    
    def __init__(self):  
        # Load the UI file into a QMainWindow instance
        self.app = QApplication(sys.argv)        
        loader = QUiLoader()
        ui_file = QFile(UI_PATH)
        ui_file.open(QIODevice.ReadOnly)
        self.main_win = loader.load(ui_file)
        ui_file.close()

        # --- Initialize classes for event binding ---
        self.search = SearchEvents()
        # Initialize the MenuActions manager
        self.menu = MenuActions() # Does not need a parent here
        self.webdriver = WebDriverToolkit()

        # --- Connect MenuActions signals to MainWindow slots ---
        # These slots will handle feedback from the background tasks
        self.menu.task_started.connect(self.on_task_started)
        self.menu.task_output.connect(self.on_task_output)
        self.menu.task_finished.connect(self.on_task_finished)

        # --- Cleanly stop the worker thread on application exit ---
        self.app.aboutToQuit.connect(self.menu.stop_worker_thread)
    
    #--------------------------------------------------------------------------
    def _connect_action(self, action_name: str, slot):        
        action = self.main_win.findChild(QAction, action_name)
        action.triggered.connect(slot)        

    #--------------------------------------------------------------------------
    def _connect_button(self, button_name: str, slot):        
        button = self.main_win.findChild(QPushButton, button_name)
        button.clicked.connect(slot)      

    #--------------------------------------------------------------------------
    def run_installer(self):
        self._connect_action("action_run_installer", self.menu.run_installation)

    #--------------------------------------------------------------------------
    def update_app(self):
        self._connect_action("action_look_for_updates", self.menu.update_from_git)

    #--------------------------------------------------------------------------
    def delete_all_logs(self):
        self._connect_action("action_remove_all_logs", self.menu.delete_all_logs)

    #--------------------------------------------------------------------------
    def developer_mode_install(self):
        self._connect_action("action_run_developer_mode_install", self.menu.run_developer_mode)

    #--------------------------------------------------------------------------
    def search_from_file(self):
        self._connect_button("searchFromFile", self.search.search_from_file)

    #--------------------------------------------------------------------------
    def verify_webdriver(self):
        self._connect_button("VerifyWD", self.webdriver.is_chromedriver_installed)

    #--------------------------------------------------------------------------
    def set_events_binding(self):       
        self.run_installer()
        self.update_app()
        self.delete_all_logs()
        self.developer_mode_install() 
        self.search_from_file()
        self.verify_webdriver()       

    #--------------------------------------------------------------------------
    # Slots to handle feedback from MenuActions
    #--------------------------------------------------------------------------
    @Slot(str)
    def on_task_started(self, task_name):
        """Called when a background task starts."""
        print(f"UI Received: Task '{task_name}' started.")
        status_bar = self.main_win.statusBar() # Assumes main_win is QMainWindow
        if status_bar:
            status_bar.showMessage(f"Running '{task_name}'...", 0) # Show indefinitely

        # Example: Disable relevant actions/buttons
        # You might want a more sophisticated way to track which actions relate to the running task
        self._set_menu_actions_enabled(False)

    @Slot(str, str)
    #--------------------------------------------------------------------------
    def on_task_output(self, task_name, output):
        """Called when a background task produces output."""
        # print(f"Output [{task_name}]: {output.strip()}") # Optionally log to console
        # Try to find a QTextEdit (e.g., named 'logOutputArea') to display logs
        log_area = self.main_win.findChild(QTextEdit, "logOutputArea")
        if log_area:
            log_area.append(output.strip())
        else:
             # Fallback to console if no log area found
             print(f"[{task_name} Output]: {output.strip()}")


    @Slot(str, bool, str)
    #--------------------------------------------------------------------------
    def on_task_finished(self, task_name, success, message):
        """Called when a background task finishes."""        
        status_bar = self.main_win.statusBar()
        if status_bar:
            status_bar.showMessage(f"Task '{task_name}' finished.", 5000) # Show for 5 seconds

        log_area = self.main_win.findChild(QTextEdit, "logOutputArea")
        final_message = f"--- Task '{task_name}' Finished ---\nSuccess: {success}\nResult: {message}\n---------------------------------"
        if log_area:
            log_area.append(final_message)
        else:
            print(final_message) # Fallback

        if not success:
            # Use QMessageBox for important failure messages
            QMessageBox.warning(self.main_win, f"Task Failed: {task_name}", message)

        # Re-enable actions/buttons
        self._set_menu_actions_enabled(True)

    #--------------------------------------------------------------------------
    def _set_menu_actions_enabled(self, enabled):        
        action_names = [
            "action_run_installer",
            "action_look_for_updates",
            "action_remove_all_logs",
            "action_run_developer_mode_install"]
        for name in action_names:
            action = self.main_win.findChild(QAction, name)
            if action:
                action.setEnabled(enabled)

        # Example: Handle a cancel button state
        # cancel_button = self.main_win.findChild(QPushButton, "cancelTaskButton")
        # if cancel_button:
        #     cancel_button.setEnabled(not enabled)
    
    #--------------------------------------------------------------------------
    def run(self):        
        self.set_events_binding()
        self.main_win.show()
        sys.exit(self.app.exec())