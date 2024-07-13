@echo off
rem Use this script to create a new environment called "EMADB"

echo STEP 1: Creation of EMADB environment
call conda create -n EMADB python=3.10 -y
if errorlevel 1 (
    echo Failed to create the environment EMADB
    goto :eof
)

rem If present, activate the environment
call conda activate EMADB


rem Install additional packages with pip
echo STEP 2: Install python libraries and packages
call pip install numpy pandas tqdm selenium webdriver-manager beautifulsoup4 
if errorlevel 1 (
    echo Failed to install Python libraries.
    goto :eof
)

@echo off
rem install packages in editable mode
echo STEP 3: Install utils packages in editable mode
call cd .. && pip install -e .
if errorlevel 1 (
    echo Failed to install the package in editable mode
    goto :eof
)

rem Print the list of dependencies installed in the environment
echo List of installed dependencies
call conda list

set/p<nul =Press any key to exit... & pause>nul
