@echo off
setlocal enabledelayedexpansion

for /f "delims=" %%i in ("%~dp0..") do set "project_folder=%%~fi"
set "env_name=EMADB"
set "project_name=EMADB"
set "env_path=%project_folder%\setup\environment\%env_name%"
set "app_path=%project_folder%\%project_name%"
set "conda_path=%project_folder%\setup\miniconda"
set "setup_path=%project_folder%\setup"


:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: Check if conda is installed
:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:check_conda
where conda >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Anaconda/Miniconda is not installed. Installing Miniconda...   
    cd /d "%conda_path%"        
    if not exist Miniconda3-latest-Windows-x86_64.exe (
        echo Downloading Miniconda 64-bit installer...
        powershell -Command "Invoke-WebRequest -Uri https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe -OutFile Miniconda3-latest-Windows-x86_64.exe"
    )    
    echo Installing Miniconda to %conda_path%
    start /wait "" Miniconda3-latest-Windows-x86_64.exe ^
        /InstallationType=JustMe ^
        /RegisterPython=0 ^
        /AddToPath=0 ^
        /S ^
        /D=%conda_path%    
    
    call "%conda_path%\Scripts\activate.bat" "%conda_path%"
    echo Miniconda installation is complete.    
    goto :check_environment

) else (
    echo Anaconda/Miniconda already installed.   
    goto :check_environment
)

:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: Check if the environment exists when not using a custom environment
:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:check_environment
if exist "%env_path%" (    
    echo Python environment '%env_name%' detected.
    goto :conda_activation

) else (
    echo Running first-time installation for %env_name%. 
    echo Please wait until completion and do not close this window!
    echo Depending on your internet connection, this may take a while...
    call "%setup_path%\install_on_windows.bat"
    goto :conda_activation
)

:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: Precheck for conda source 
:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:conda_activation
where conda >nul 2>&1
if %ERRORLEVEL% neq 0 (   
    call "%conda_path%\Scripts\activate.bat" "%conda_path%"      
    goto :main_menu
) 

:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: Show main menu
:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:main_menu
echo.
echo ==========================================================================
echo               EMAutoPilot
echo ==========================================================================
echo 1. Download EMA drugs adverse reactions report 
echo 2. Find ATC codes for drugs
echo 3. Look for drug-to-drug interactions (DDIs)
echo 4. Setup and Maintenance
echo 5. Exit
echo.
set /p choice="Select an option (1-5): "

if "%choice%"=="1" goto :autopilot
if "%choice%"=="2" goto :ATC
if "%choice%"=="3" goto :interactions
if "%choice%"=="4" goto :setup_menu
if "%choice%"=="5" goto exit
echo Invalid option, try again.
goto :main_menu

:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: Run download EMA reports
:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:autopilot
cls
start cmd /k "call conda activate "%env_path%" && python "%app_path%"\services\download_EMA_reports.py"
pause
goto :main_menu

:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: Run download EMA reports
:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:ATC
cls
start cmd /k "call conda activate "%env_path%" && python "%app_path%"\services\ATC_mapper.py"
pause
goto :main_menu

:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: Run download EMA reports
:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:interactions
cls
start cmd /k "call conda activate "%env_path%" && python "%app_path%"\services\find_drugs_interactions.py"
pause
goto :main_menu

:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: Show setup menu
:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:setup_menu
cls
echo ==========================================================================
echo                         Setup  and Maintenance                          
echo ==========================================================================
echo 1. Install project in editable mode
echo 2. Update project
echo 3. Remove logs
echo 4. Back to main menu
echo.
set /p sub_choice="Select an option (1-4): "

if "%sub_choice%"=="1" goto :eggs
if "%sub_choice%"=="2" goto :update
if "%sub_choice%"=="3" goto :logs
if "%sub_choice%"=="4" goto :main_menu
echo Invalid option, try again.
goto :setup_menu

:eggs
call conda activate "%env_path%" && cd "%project_folder%" && pip install -e . --use-pep517
pause
goto :setup_menu

:update
cd "%project_folder%"
call git pull
if errorlevel 1 (
    echo Error: Git pull failed.
    pause
    goto :setup_menu
)
pause
goto :setup_menu

:logs
cd "%app_path%\resources\logs" 
if not exist *.log (
    echo No log files found.
    pause
    goto :setup_menu
)
del *.log /q
echo Log files deleted.
pause
goto :setup_menu
