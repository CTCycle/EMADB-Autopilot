@echo off
setlocal enabledelayedexpansion

set "env_name=EMADB"
set "project_name=EMADB"

:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: Check if conda is installed
:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:check_conda
where conda >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Anaconda/Miniconda is not installed. Installing Miniconda...   
    cd /d "%~dp0"        
    if not exist Miniconda3-latest-Windows-x86_64.exe (
        echo Downloading Miniconda 64-bit installer...
        powershell -Command "Invoke-WebRequest -Uri https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe -OutFile Miniconda3-latest-Windows-x86_64.exe"
    )    
    echo Installing Miniconda to %USERPROFILE%\Miniconda3
    start /wait "" Miniconda3-latest-Windows-x86_64.exe ^
        /InstallationType=JustMe ^
        /RegisterPython=0 ^
        /AddToPath=0 ^
        /S ^
        /D=%~dp0setup\miniconda    
    
    call "%~dp0..\setup\miniconda\Scripts\activate.bat" "%~dp0..\setup\miniconda"
    echo Miniconda installation is complete.    
    goto :initial_check

) else (
    echo Anaconda/Miniconda already installed. Checking python environment...    
    goto :initial_check
)

:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: Check if the environment exists when not using a custom environment
:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:initial_check   
cd /d "%~dp0\.."

:check_environment
set "env_path=.setup\environment\%env_name%"

if exist ".setup\environment\%env_name%\" (    
    echo Python environment '%env_name%' detected.
    goto :conda_activation

) else (
    echo Running first-time installation for %env_name%. 
    echo Please wait until completion and do not close this window!
    echo Depending on your internet connection, this may take a while...
    call ".\setup\install_on_windows.bat"
    goto :conda_activation
)

:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: Precheck for conda source 
:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:conda_activation
where conda >nul 2>&1
if %ERRORLEVEL% neq 0 (   
    call "%~dp0..\setup\miniconda\Scripts\activate.bat" "%~dp0..\setup\miniconda"       
    goto :main_menu
) 

:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: Show main menu
:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:main_menu
echo.
echo =======================================
echo               EMAutoPilot
echo =======================================
echo 1. Start EMAutoPilot 
echo 2. Setup and Maintenance
echo 3. Exit
echo.
set /p choice="Select an option (1-3): "

if "%choice%"=="1" goto :main
if "%choice%"=="2" goto :setup_menu
if "%choice%"=="3" goto exit
echo Invalid option, try again.
pause
goto :main_menu

:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: Run main app
:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:main
cls
call conda activate %env_name% && python .\commons\main.py
pause
goto :main_menu

:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: Show setup menu
:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:setup_menu
cls
echo =======================================
echo         Setup and Maintenance
echo =======================================
echo 1. Install project in editable mode
echo 2. Remove logs
echo 3. Back to main menu
echo.
set /p sub_choice="Select an option (1-3): "

if "%sub_choice%"=="1" goto :eggs
if "%sub_choice%"=="2" goto :logs
if "%sub_choice%"=="3" goto :main_menu
echo Invalid option, try again.
pause
goto :setup_menu

:eggs
call conda activate --prefix %env_path% && cd .. && pip install -e . --use-pep517 && cd %project_name%
pause
goto :setup_menu

:logs
cd /d "%~dp0..\%project_name%\resources\logs"
del *.log /q
cd ..\..
pause
goto :setup_menu
