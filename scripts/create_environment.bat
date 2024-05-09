@echo off
rem Use this script to create a new environment called "EMA-DB"

echo STEP 1: Creation of EMA-DB environment
call conda create -n EMA-DB python=3.10 
if errorlevel 1 (
    echo Failed to create the environment FEXT
    goto :eof
)

echo Environment EMA-DB successfully created!
rem If present, activate the environment
call conda activate EMA-DB


rem Install additional packages with pip
echo STEP 2: Install python libraries and packages
call pip install numpy pandas tqdm selenium webdriver-manager beautifulsoup4 
if errorlevel 1 (
    echo Failed to install Python libraries.
    goto :eof
)

rem Print the list of dependencies installed in the environment
echo List of installed dependencies
call conda list

set/p<nul =Press any key to exit... & pause>nul
