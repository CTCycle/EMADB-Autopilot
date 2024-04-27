@echo off
rem Use this script to create a new environment called "DC_interact"

echo STEP 1: Creation of DC_interact environment
call conda create -n DC_interact python=3.10 
if errorlevel 1 (
    echo Failed to create the environment FEXT
    goto :eof
)

echo Environment DC_interact successfully created!
rem If present, activate the environment
call conda activate DC_interact


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
