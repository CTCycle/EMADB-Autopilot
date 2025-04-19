import os
import sys
from PySide6.QtCore import QObject, Signal, QProcess, QThread, QTimer, Slot

from EMADB.commons.constants import ROOT_DIR, LOGS_PATH, SETUP_PATH
from EMADB.commons.logger import logger





###############################################################################
class MenuActionsWorker(QObject):   
    # Signals (use PySide6 'Signal')
    # finished(task_name, success, message)
    finished = Signal(str, bool, str)
    # Emits output from processes (stdout/stderr)
    outputReady = Signal(str, str)
    # Signals start of a task
    taskStarted = Signal(str)

    def __init__(self, installer_path, python_env_name, root_dir, logs_path, parent=None):
        super().__init__(parent)
        self.installer_path = installer_path
        self.python_env_name = python_env_name
        self.root_dir = root_dir
        self.logs_path = logs_path
        self._process = None # To hold the currently running QProcess

    #--------------------------------------------------------------------------
    def _run_process(self, task_name, program, arguments=None, working_directory=None):        
        if self._process and self._process.state() != QProcess.ProcessState.NotRunning:
            self.finished.emit(task_name, False, "Another process is already running.")
            return

        self.taskStarted.emit(task_name)
        self._process = QProcess()
        if working_directory:
            self._process.setWorkingDirectory(working_directory)

        # Combine stdout and stderr for simplicity, or handle separately
        self._process.readyReadStandardOutput.connect(lambda: self._handle_output(task_name))
        self._process.readyReadStandardError.connect(lambda: self._handle_error_output(task_name))
        # Use lambda for finished signal to capture task_name correctly
        self._process.finished.connect(lambda exit_code, exit_status: self._handle_finished(task_name, exit_code, exit_status))
        # Handle errors like command not found
        self._process.errorOccurred.connect(lambda error: self._handle_process_error(task_name, error))

        print(f"Starting process for task '{task_name}': {program} {arguments}") # Debug print
        if arguments:
            self._process.start(program, arguments)
        else:
            # For commands needing shell interpretation
            if sys.platform == "win32":
                self._process.start("cmd", ["/c", program])
            else:
                self._process.start("sh", ["-c", program])

    #--------------------------------------------------------------------------
    def _handle_output(self, task_name):
        if not self._process: return
        # readAllStandardOutput returns QByteArray, convert to bytes then decode
        output = bytes(self._process.readAllStandardOutput()).decode(errors='ignore')
        if output:
            self.outputReady.emit(task_name, output)

    #--------------------------------------------------------------------------
    def _handle_error_output(self, task_name):
        if not self._process: return
        # readAllStandardError returns QByteArray, convert to bytes then decode
        error_output = bytes(self._process.readAllStandardError()).decode(errors='ignore')
        if error_output:
            self.outputReady.emit(task_name, f"ERROR: {error_output}")

    #--------------------------------------------------------------------------
    def _handle_finished(self, task_name, exit_code, exit_status):
        if not self._process: return # Prevent issues if called after process is cleared

        # Read any remaining output before processing finish status
        self._handle_output(task_name)
        self._handle_error_output(task_name)

        # Use QProcess.ExitStatus enum
        if exit_status == QProcess.ExitStatus.NormalExit and exit_code == 0:
            success = True
            message = f"Task '{task_name}' completed successfully."
        elif exit_status == QProcess.ExitStatus.CrashExit:
            success = False
            message = f"Task '{task_name}' crashed."
        else:
            success = False
            message = f"Task '{task_name}' failed with exit code {exit_code}."

        print(message) # Debug print
        self.finished.emit(task_name, success, message)
        # Important: Disconnect signals before deleting or clearing the process
        # to avoid potential issues if signals arrive late.
        try:
            self._process.disconnect(self) # Disconnect all connections from self
        except (TypeError, RuntimeError): # Catch potential errors during disconnect
            pass
        self._process = None # Allow new process to run

    #--------------------------------------------------------------------------
    def _handle_process_error(self, task_name, error):
        # Use QProcess.ProcessError enum
         if not self._process: return
         error_map = {
             QProcess.ProcessError.FailedToStart: "Failed to start",
             QProcess.ProcessError.Crashed: "Crashed",
             QProcess.ProcessError.Timedout: "Timed out",
             QProcess.ProcessError.ReadError: "Read error",
             QProcess.ProcessError.WriteError: "Write error",
             QProcess.ProcessError.UnknownError: "Unknown error"}
         
         error_string = error_map.get(error, "Unknown error occurred")
         process_error_string = self._process.errorString() # Get specific error message
         message = f"Process error for task '{task_name}': {error_string} - {process_error_string}"
         print(message) # Debug print

         # Check state before emitting finished to avoid duplicates if _handle_finished also runs
         current_process = self._process
         if current_process and current_process.state() == QProcess.ProcessState.NotRunning:
            try:
                current_process.disconnect(self)
            except (TypeError, RuntimeError):
                 pass
            self.finished.emit(task_name, False, message)
            if self._process == current_process: # Ensure it hasn't been changed by another call
                self._process = None

    # --- Public Slots to Trigger Tasks (Use PySide6 'Slot') ---
    #--------------------------------------------------------------------------
    @Slot()
    def run_installation(self):
        """Runs the installation script using QProcess."""
        task_name = "installation"
        self._run_process(task_name, self.installer_path)

    @Slot()
    #--------------------------------------------------------------------------
    def run_developer_mode(self):
        """Runs conda activate and pip install using QProcess."""
        task_name = "developer_mode"
        # Same caveat as before: 'conda activate' is tricky. A temp script is more robust.
        cmd = f'conda activate "{self.python_env_name}" && cd /d "{self.root_dir}" && pip install -e . --use-pep517'
        self._run_process(task_name, cmd)
        # Consider implementing the temporary script alternative from the previous answer if this fails.

    @Slot()
    #--------------------------------------------------------------------------
    def update_from_git(self):
        """Runs git pull using QProcess."""
        task_name = "git_update"
        self._run_process(task_name, "git", ["pull"], working_directory=self.root_dir)

    @Slot()
    #--------------------------------------------------------------------------
    def delete_all_logs(self):
        """Deletes all .log files in the specified directory."""
        task_name = "delete_logs"
        self.taskStarted.emit(task_name)
        print(f"Starting task '{task_name}'") # Debug print
        try:
            log_files = [f for f in os.listdir(self.logs_path) if f.lower().endswith('.log')]
            if not log_files:
                self.finished.emit(task_name, True, "No log files found to delete.")
                return

            deleted_count = 0
            errors = []
            for name in log_files:
                file_path = os.path.join(self.logs_path, name)
                try:
                    os.remove(file_path)
                    deleted_count += 1
                except OSError as e:
                    error_msg = f"Could not delete {name}: {e}"
                    print(error_msg) # Debug print error
                    errors.append(error_msg)

            if errors:
                message = f"Deleted {deleted_count} log files. Errors occurred:\n" + "\n".join(errors)
                self.finished.emit(task_name, False, message)
            else:
                message = f"Successfully deleted {deleted_count} log files."
                self.finished.emit(task_name, True, message)

        except Exception as e:
            message = f"Error accessing log directory '{self.logs_path}': {e}"
            print(message) # Debug print error
            self.finished.emit(task_name, False, message)

    @Slot()
    #--------------------------------------------------------------------------
    def stop_process(self):
        """Attempts to stop the currently running QProcess."""
        if self._process and self._process.state() != QProcess.ProcessState.NotRunning:
            print("Attempting to terminate process...")
            self._process.terminate()
            # Use QTimer for delayed kill check
            QTimer.singleShot(1000, self._kill_if_running)

    #--------------------------------------------------------------------------
    def _kill_if_running(self):
        # Check if the same process instance is still running
        if self._process and self._process.state() != QProcess.ProcessState.NotRunning:
            print("Process did not terminate, killing...")
            self._process.kill()
            # Ensure the finished signal is emitted if killed abruptly
            # This might not be needed if QProcess emits finished on kill, but can be a safeguard
            # QTimer.singleShot(100, lambda: self._check_killed_state(self._process)) # Check shortly after

    # Optional: Check state after kill, might not be necessary
    # def _check_killed_state(self, process_instance):
    #      if process_instance and process_instance.state() != QProcess.NotRunning:
    #          print(f"Warning: Process {process_instance.processId()} may not have been killed.")
    #      # Consider emitting a 'finished' signal here if QProcess doesn't always do it on kill
       
        


###############################################################################
class MenuActions(QObject):    
    # Signals to relay information to the UI (use PySide6 'Signal')
    task_started = Signal(str)
    task_output = Signal(str, str) # task_name, output_text
    task_finished = Signal(str, bool, str) # task_name, success, message

    def __init__(self, parent=None):
        super().__init__(parent)
        # Assume SETUP_PATH, ROOT_DIR, LOGS_PATH are accessible
        self.installer_path = os.path.join(SETUP_PATH, 'install_on_windows.bat')
        self.python_env_name = os.path.join(SETUP_PATH, 'environment', 'EMADB')
        self.root_dir = ROOT_DIR
        self.logs_path = LOGS_PATH

        self._worker_thread = QThread(self)
        self._worker = MenuActionsWorker(
            self.installer_path,
            self.python_env_name,
            self.root_dir,
            self.logs_path)
        
        self._worker.moveToThread(self._worker_thread)

        # --- Connect worker signals to manager slots (or relay signals) ---
        self._worker.taskStarted.connect(self.on_task_started)
        self._worker.outputReady.connect(self.on_task_output)
        self._worker.finished.connect(self.on_task_finished)

        # Clean up thread
        # self._worker_thread.finished.connect(self._worker.deleteLater) # deleteLater good practice
        self.destroyed.connect(self.stop_worker_thread)

        self._worker_thread.start()

    #--------------------------------------------------------------------------
    def stop_worker_thread(self):        
        if self._worker_thread.isRunning():
            print("Stopping worker thread...")
            # Request worker to stop its process first
            # Use QMetaObject.invokeMethod for thread-safe call if needed,
            # but direct call often works if worker event loop is running.
            # For safety, let's ensure it's queued if called from main thread
            self._worker.stop_process() # This call should be queued automatically

            self._worker_thread.quit()
            if not self._worker_thread.wait(3000): # Wait up to 3 seconds
                 print("Worker thread did not quit gracefully, terminating.")
                 self._worker_thread.terminate()
                 self._worker_thread.wait() # Wait after terminate too
            print("Worker thread stopped.")
        # Optionally delete worker after thread stops fully
        self._worker.deleteLater()

    # --- Slots to receive signals from the worker (Use PySide6 'Slot') ---

    @Slot(str)
    #--------------------------------------------------------------------------
    def on_task_started(self, task_name):
        print(f"Manager received: Task '{task_name}' started.")
        self.task_started.emit(task_name)
        # Example UI update: self.parent().statusBar().showMessage(...)
        # Example UI update: self.parent().set_buttons_enabled(False)

    @Slot(str, str)
    #--------------------------------------------------------------------------
    def on_task_output(self, task_name, output):
        self.task_output.emit(task_name, output)
        # Example UI update: self.parent().log_text_edit.append(output)

    @Slot(str, bool, str)
    #--------------------------------------------------------------------------
    def on_task_finished(self, task_name, success, message):
        print(f"Manager received: Task '{task_name}' finished. Success: {success}. Message: {message}")
        self.task_finished.emit(task_name, success, message)
        # Example UI update: self.parent().statusBar().showMessage(message, 5000)
        # Example UI update: self.parent().set_buttons_enabled(True)

    # --- Public methods called by the UI to trigger tasks ---
    # No Slot decorator needed here as these are called directly from Python

    #--------------------------------------------------------------------------
    def run_installation(self):    
        # Call the worker's slot. This will be queued automatically
        # because the worker lives in a different thread.
        self._worker.run_installation()

    #--------------------------------------------------------------------------
    def run_developer_mode(self):
        self._worker.run_developer_mode()

    #--------------------------------------------------------------------------
    def update_from_git(self):
        self._worker.update_from_git()

    #--------------------------------------------------------------------------
    def delete_all_logs(self):
        self._worker.delete_all_logs()

    #--------------------------------------------------------------------------
    def cancel_current_task(self):        
        self._worker.stop_process() 
               
