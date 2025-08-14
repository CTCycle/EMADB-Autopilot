@echo off
setlocal enabledelayedexpansion

REM ============================================================================
REM == Configuration: define project and Python paths
REM ============================================================================
set "project_folder=%~dp0"
set "root_folder=%project_folder%..\"
set "python_dir=%project_folder%setup\python"
set "python_exe=%python_dir%\python.exe"
set "pip_exe=%python_dir%\Scripts\pip.exe"
set "env_marker=%python_dir%\.is_installed"
set "app_script=%project_folder%app\app.py"
set "requirements_path=%project_folder%setup\requirements.txt"

REM ============================================================================
REM == 0. Fast path: skip full setup if environment already present
REM ============================================================================
if exist "%env_marker%" if exist "%python_exe%" if exist "%pip_exe%" (
    echo [INFO] Environment already installed. Skipping setup.
    goto :run_app
)

REM ============================================================================
REM == 1. Full environment setup
REM ============================================================================
echo [STEP 1/3] Setting up Python environment...

REM --- Dynamic variables for Python distribution
set "python_version=3.12.10"
set "python_major_version=3"
set "python_minor_version=12"
set "python_zip_filename=python-%python_version%-embed-amd64.zip"
set "python_zip_url=https://www.python.org/ftp/python/%python_version%/%python_zip_filename%"
set "python_zip_path=%python_dir%\%python_zip_filename%"
set "python_pth_file=%python_dir%\python%python_major_version%%python_minor_version%._pth"
set "get_pip_url=https://bootstrap.pypa.io/get-pip.py"
set "get_pip_path=%python_dir%\get-pip.py"

REM Create Python directory
mkdir "%python_dir%" 2>nul

REM Download and extract embeddable Python
powershell -Command "(New-Object System.Net.WebClient).DownloadFile('%python_zip_url%', '%python_zip_path%')" || goto :error
powershell -Command "Expand-Archive -Path '%python_zip_path%' -DestinationPath '%python_dir%' -Force" || goto :error
del "%python_zip_path%"

REM Bootstrap pip
powershell -Command "(Get-Content '%python_pth_file%') -replace '#import site','import site' | Set-Content '%python_pth_file%'" || goto :error
powershell -Command "(New-Object System.Net.WebClient).DownloadFile('%get_pip_url%', '%get_pip_path%')" || goto :error
"%python_exe%" "%get_pip_path%" || goto :error
del "%get_pip_path%"

REM ============================================================================
REM == 1b. Install dependencies
REM ============================================================================
echo [STEP 2/3] Installing dependencies...
if not exist "%requirements_path%" (
    echo [FATAL] requirements.txt not found: "%requirements_path%"
    goto :error
)

echo [INFO] Upgrading pip package
"%pip_exe%" install --upgrade pip >nul 2>&1 || goto :error

echo [INFO] Installing requirements
"%pip_exe%" install --no-warn-script-location -r "%requirements_path%" || goto :error

echo [INFO] Installing setuptools and wheel
"%pip_exe%" install --no-warn-script-location setuptools wheel || goto :error

pushd "%root_folder%"
echo [INFO] Installing project in editable mode
"%pip_exe%" install -e . --use-pep517 || (popd & goto :error)
popd

"%pip_exe%" cache purge || goto :error

REM Mark environment as installed for future fast start
> "%env_marker%" echo setup_completed

echo [SUCCESS] Environment setup complete.

REM ============================================================================
REM == 2. Run the application
REM ============================================================================
:run_app
echo [STEP 3/3] Running application...
if not exist "%app_script%" (
    echo [FATAL] Application script not found: "%app_script%"
    goto :error
)

pushd "%root_folder%"
"%python_exe%" "%app_script%" || (popd & goto :error)
popd
echo [SUCCESS] Application launched successfully.

endlocal
exit /b 0

REM ============================================================================
REM == Error handling
REM ============================================================================
:error
echo.
echo !!! An error occurred during execution. !!!
pause
endlocal
exit /b 1