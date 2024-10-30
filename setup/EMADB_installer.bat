@echo off

:: [INSTALL DEPENDENCIES] 
:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: Check if NVIDIA GPU is available using nvidia-smi
:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
call conda config --add channels conda-forge
call conda info --envs | findstr "EMADB"
if %ERRORLEVEL%==0 (
    echo EMADB environment detected
    call conda activate EMADB
    goto :dependencies
) else (
    echo EMADB environment has not been found, it will now be created using python 3.11
    echo Depending on your internet connection, this may take a while!
    call conda create -n EMADB python=3.11 -y
    call conda activate EMADB
    goto :dependencies
)

:: [INSTALL DEPENDENCIES] 
:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: Check if NVIDIA GPU is available using nvidia-smi
:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:dependencies
echo.
echo Install python libraries and packages
call pip install numpy==2.1.2 pandas==2.2.3 tqdm==4.66.4
call pip install selenium==4.23.0 webdriver-manager==4.0.1 beautifulsoup4==4.12.3 

:: [INSTALL PROJECT IN EDITABLE MODE] 
:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: Check if NVIDIA GPU is available using nvidia-smi
:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
echo Install utils packages in editable mode
call cd .. && pip install -e . --use-pep517 && cd EMADB

:: [CLEAN CACHE] 
:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: Check if NVIDIA GPU is available using nvidia-smi
:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
echo.
echo Cleaning conda and pip cache 
call conda clean --all -y
call pip cache purge

:: [SHOW LIST OF INSTALLED DEPENDENCIES]
:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: Check if NVIDIA GPU is available using nvidia-smi
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::: 
echo.
echo List of installed dependencies:
call conda list

echo.
echo Installation complete. You can now run EMADB on this system!
pause
