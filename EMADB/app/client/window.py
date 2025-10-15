from __future__ import annotations
from typing import cast
from collections.abc import Callable

from EMADB.app.variables import EnvironmentVariables

EV = EnvironmentVariables()

from functools import partial

from PySide6.QtCore import QFile, QIODevice, QThreadPool, Slot
from PySide6.QtGui import QAction
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
)
from qt_material import apply_stylesheet

from EMADB.app.client.dialogs import LoadConfigDialog, SaveConfigDialog
from EMADB.app.client.events import SearchEvents
from EMADB.app.client.workers import Worker
from EMADB.app.configuration import Configuration
from EMADB.app.logger import logger
from EMADB.app.utils.services.toolkit import WebDriverToolkit


###############################################################################
def apply_style(app: QApplication) -> QApplication:
    theme = "dark_yellow"
    extra = {"density_scale": "-1"}
    apply_stylesheet(app, theme=f"{theme}.xml", extra=extra)

    # Make % text visible/centered for ALL progress bars
    app.setStyleSheet(
        app.styleSheet()
        + """
    QProgressBar {
        text-align: center;   /* align percentage to the center */
        color: black;        /* black text for yellow bar */
        font-weight: bold;   /* bold percentage */        
    }
    """
    )

    return app


###############################################################################
class MainWindow:
    def __init__(self, ui_file_path: str) -> None:
        super().__init__()
        loader = QUiLoader()
        ui_file = QFile(ui_file_path)
        ui_file.open(QIODevice.OpenModeFlag.ReadOnly)
        self.main_win = cast(QMainWindow, loader.load(ui_file))
        ui_file.close()

        # initial settings
        self.config_manager = Configuration()
        self.configuration = self.config_manager.get_configuration()

        # set thread pool for the workers
        self.threadpool = QThreadPool.globalInstance()
        self.worker = None
        self.worker_running = False

        # --- Create persistent handlers ---
        self.search_handler = SearchEvents(self.configuration)
        self.webdriver = WebDriverToolkit(headless=True, ignore_SSL=False)

        # setup UI elements
        self.set_states()
        self.widgets = {}
        self.setup_configuration(
            [
                # actions
                (QAction, "actionLoadConfig", "load_configuration_action"),
                (QAction, "actionSaveConfig", "save_configuration_action"),
                (QPushButton, "stopSearch", "stop_search"),
                (QCheckBox, "headless", "headless"),
                (QCheckBox, "IgnoreSSL", "ignore_SSL"),
                (QDoubleSpinBox, "waitTime", "wait_time"),
                (QPlainTextEdit, "drugInputs", "text_drug_inputs"),
                (QPushButton, "searchFromFile", "search_file"),
                (QPushButton, "searchFromBox", "search_box"),
                (QPushButton, "checkDriver", "check_driver"),
            ]
        )
        self.connect_signals(
            [
                # actions
                ("save_configuration_action", "triggered", self.save_configuration),
                ("load_configuration_action", "triggered", self.load_configuration),
                ("stop_search", "clicked", self.stop_running_worker),
                ("search_file", "clicked", self.search_from_file),
                ("search_box", "clicked", self.search_from_text),
                ("check_driver", "clicked", self.check_webdriver),
            ]
        )

        self.auto_connect_settings()

    # [SHOW WINDOW]
    ###########################################################################
    def show(self) -> None:
        self.main_win.show()

    # [HELPERS]
    ###########################################################################
    def connect_update_setting(
        self, widget, signal_name, config_key, getter=None
    ) -> None:
        if getter is None:
            if isinstance(widget, (QCheckBox)):
                getter = widget.isChecked
            elif isinstance(widget, (QDoubleSpinBox)):
                getter = widget.value

        signal = getattr(widget, signal_name)
        signal.connect(partial(self.update_single_setting, config_key, getter))

    # -------------------------------------------------------------------------
    def update_single_setting(self, config_key, getter, *args) -> None:
        value = getter()
        self.config_manager.update_value(config_key, value)

    # -------------------------------------------------------------------------
    def auto_connect_settings(self) -> None:
        connections = [
            ("headless", "toggled", "headless"),
            ("ignore_SSL", "toggled", "ignore_SSL"),
            ("wait_time", "valueChanged", "wait_time"),
        ]

        for attr, signal_name, config_key in connections:
            widget = self.widgets[attr]
            self.connect_update_setting(widget, signal_name, config_key)

    # -------------------------------------------------------------------------
    def set_states(self) -> None:
        pass

    # -------------------------------------------------------------------------
    def connect_button(self, button_name: str, slot) -> None:
        button: QPushButton | None = self.main_win.findChild(
            QPushButton, button_name
        )
        if button is None:
            raise LookupError(f"Button '{button_name}' not found.")
        button.clicked.connect(slot) if button else None

    # -------------------------------------------------------------------------
    def start_worker(
        self, worker: Worker, on_finished : Callable, on_error : Callable, on_interrupted
    ) -> None:
        worker.signals.finished.connect(on_finished)
        worker.signals.error.connect(on_error)
        worker.signals.interrupted.connect(on_interrupted)
        self.threadpool.start(worker)
        self.worker_running = True

    # -------------------------------------------------------------------------
    def send_message(self, message) -> None:
        self.main_win.statusBar().showMessage(message)

    # [SETUP]
    ###########################################################################
    def setup_configuration(self, widget_defs) -> None:
        for cls, name, attr in widget_defs:
            w = self.main_win.findChild(cls, name)
            setattr(self, attr, w)
            self.widgets[attr] = w

    # -------------------------------------------------------------------------
    def connect_signals(self, connections) -> None:
        for attr, signal, slot in connections:
            widget = self.widgets[attr]
            getattr(widget, signal).connect(slot)

    # -------------------------------------------------------------------------
    def set_widgets_from_configuration(self) -> None:
        cfg = self.config_manager.get_configuration()
        for attr, widget in self.widgets.items():
            if attr not in cfg:
                continue
            v = cfg[attr]

            if hasattr(widget, "setChecked") and isinstance(v, bool):
                widget.setChecked(v)
            elif hasattr(widget, "setValue") and isinstance(v, (int, float)):
                widget.setValue(v)
            elif hasattr(widget, "setPlainText") and isinstance(v, str):
                widget.setPlainText(v)
            elif hasattr(widget, "setText") and isinstance(v, str):
                widget.setText(v)
            elif isinstance(widget, QComboBox):
                if isinstance(v, str):
                    idx = widget.findText(v)
                    if idx != -1:
                        widget.setCurrentIndex(idx)
                    elif widget.isEditable():
                        widget.setEditText(v)
                elif isinstance(v, int) and 0 <= v < widget.count():
                    widget.setCurrentIndex(v)

    # [SLOT]
    ###########################################################################
    # It's good practice to define methods that act as slots within the class
    # that manages the UI elements. These slots can then call methods on the
    # handler objects. Using @Slot decorator is optional but good practice
    # -------------------------------------------------------------------------
    @Slot()
    def stop_running_worker(self) -> None:
        if self.worker is not None:
            self.worker.stop()
        self.send_message("Interrupt requested. Waiting for threads to stop...")

    # -------------------------------------------------------------------------
    # [ACTIONS]
    # -------------------------------------------------------------------------
    @Slot()
    def save_configuration(self) -> None:
        dialog = SaveConfigDialog(self.main_win)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            name = dialog.get_name()
            name = "default_config" if not name else name
            self.config_manager.save_configuration_to_json(name)
            self.send_message(f"Configuration [{name}] has been saved")

    # -------------------------------------------------------------------------
    @Slot()
    def load_configuration(self) -> None:
        dialog = LoadConfigDialog(self.main_win)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            name = dialog.get_selected_config()
            if name:
                self.config_manager.load_configuration_from_json(name)
                self.set_widgets_from_configuration()
                self.send_message(f"Loaded configuration [{name}]")

    # -------------------------------------------------------------------------
    @Slot()
    def search_from_file(self) -> None:
        if self.worker_running:
            return

        self.configuration = self.config_manager.get_configuration()
        self.search_handler = SearchEvents(self.configuration)
        # functions that are passed to the worker will be executed in a separate thread
        self.worker = Worker(self.search_handler.search_using_webdriver)

        # start worker and inject signals
        self.start_worker(
            self.worker,
            on_finished=self.on_search_finished,
            on_error=self.on_error,
            on_interrupted=self.on_task_interrupted,
        )

    # -------------------------------------------------------------------------
    @Slot()
    def search_from_text(self) -> None:
        if self.worker_running:
            return

        text_box = self.main_win.findChild(QPlainTextEdit, "drugInputs")
        if not text_box:
            return

        query = text_box.toPlainText()
        drug_list = None if not query else query.strip(",")
        if drug_list is None:
            logger.warning(
                "No drug names in the text box. Proceeding with file screening..."
            )

        self.configuration = self.config_manager.get_configuration()
        self.search_handler = SearchEvents(self.configuration)

        # functions that are passed to the worker will be executed in a separate thread
        self.worker = Worker(self.search_handler.search_using_webdriver, drug_list)

        # start worker and inject signals
        self.start_worker(
            self.worker,
            on_finished=self.on_search_finished,
            on_error=self.on_error,
            on_interrupted=self.on_task_interrupted,
        )

    # -------------------------------------------------------------------------
    @Slot()
    def check_webdriver(self) -> None:
        if self.webdriver.is_chromedriver_installed():
            version = self.webdriver.check_chrome_version()
            message = f"Chrome driver is installed, current version: {version}"
            QMessageBox.information(
                self.main_win,
                "Chrome driver is installed",
                message,
                QMessageBox.StandardButton.Ok,
            )
        else:
            message = "Chrome driver is not installed, it will be installed automatically when running search"
            QMessageBox.critical(self.main_win, "Chrome driver not installed", message)

    ###########################################################################
    # [POSITIVE OUTCOME HANDLERS]
    ###########################################################################
    @Slot(object)
    def on_search_finished(self) -> None:
        message = "Search for drugs is finished, please check your downloads"
        self.send_message(message)
        if self.worker:
            self.worker = self.worker.cleanup() if self.worker else None

    ###########################################################################
    # [NEGATIVE OUTCOME HANDLERS]
    ###########################################################################
    @Slot()
    def on_error(self, err_tb) -> None:
        exc, tb = err_tb
        logger.error(f"{exc}\n{tb}")
        message = "An error occurred during the operation. Check the logs for details."
        QMessageBox.critical(self.main_win, "Something went wrong!", message)
        if self.worker:
            self.worker = self.worker.cleanup() if self.worker else None

    ###########################################################################
    # [INTERRUPTION HANDLERS]
    ###########################################################################
    def on_task_interrupted(self) -> None:
        self.send_message("Current task has been interrupted by user")
        logger.warning("Current task has been interrupted by user")
        if self.worker:
            self.worker = self.worker.cleanup() if self.worker else None
