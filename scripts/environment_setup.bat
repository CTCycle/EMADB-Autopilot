@echo off
rem Use this script to create a new environment called "EMADB"

echo STEP 1: Creation of EMADB environment
call conda create -n EMADB python=3.11 -y
if errorlevel 1 (
    echo Failed to create the environment EMADB
    goto :eof
)

rem If present, activate the environment
call conda activate EMADB

rem Install additional packages with pip
echo STEP 2: Install python libraries and packages
call pip install numpy==1.26.4 pandas==2.1.4 openpyxl==3.1.5 tqdm==4.66.4
call pip install selenium==4.23.0 webdriver-manager==4.0.1 beautifulsoup4==4.12.3 
if errorlevel 1 (
    echo Failed to install Python libraries.
    goto :eof
)

@echo off
rem install packages in editable mode
echo STEP 3: Install utils packages in editable mode
call cd .. && pip install -e . --use-pep517
if errorlevel 1 (
    echo Failed to install the package in editable mode
    goto :eof
)

rem Clean cache
echo Cleaning conda and pip cache 
call conda clean -all -y
call pip cache purge

rem Print the list of dependencies installed in the environment
echo List of installed dependencies
call conda list

set/p<nul =Press any key to exit... & pause>nul
