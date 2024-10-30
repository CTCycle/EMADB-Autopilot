# EMADB AutoPilot

## 1. Project Overview
This project is aimed at developing a script to autonomously navigate the EMA database of EudraVigilance (European Database of suspected adverse drug reactions reports). EudraVigilance is a data processing network and management system for reporting and evaluating suspected adverse drug reactions (ADRs) during the development, and following the marketing authorization of medicinal products in the European Economic Area (EEA). The system supports the electronic exchange of suspected adverse drug reaction reports known as Individual Case Safety Reports (ICSRs) between the European Medicines Agency (EMA), National Competent Authorities (NCAs), Marketing Authorization Holders (MAHs), and sponsors of clinical trials in the EEA. 

This automated system will navigate to https://www.adrreports.eu/en/search.html and look for target drugs, which are found by looking at drugs name in a .txt file within the data folder (the file can have any name). Then, it downloads data reports in the form of excel files. The script is based on chromedriver, meaning that it will simulate a user interacting with a browser to navigate the online database. 

## 2. Installation
The installation process on Windows has been designed for simplicity and ease of use. To begin, simply run `EMAutoPilot.bat`. On its first execution, the installation procedure will automatically start with minimal user input required. The script will check if either Anaconda or Miniconda is installed on your system. If neither is found, you will need to install it manually. You can download and install Miniconda by following the instructions here: (https://docs.anaconda.com/miniconda/).

After setting up Anaconda/Miniconda, the installation script will install all the necessary Python dependencies. If you'd prefer to handle the installation process separately, you can run the standalone installer by executing `setup/EMADB_installer.bat`. You can also use a custom python environment by modifying `settings/launcher_configurations.ini` and setting use_custom_environment as true, while specifying the name of your custom environment.

**Important:** After installation, if the project folder is moved or its path is changed, the application will no longer function correctly. To fix this, you can either:

- Open the main menu, select "EMADB setup," and choose "Install project packages"
- Manually run the following commands in the terminal, ensuring the project folder is set as the current working directory (CWD):

    `conda activate EMADB`

    `pip install -e . --use-pep517` 

## 3. How to use
On Windows, run `EMADB.bat` to launch the main navigation menu and browse through the various options. Alternatively, you can launch the main app file running `python EMADB/commons/main.py`. 

### 3.1 Navigation menu

**1) Run EMAutoPilot:** run the main application and start the start the automated browser. Since the script is based on Chromedriver, your need to have Google Chrome browser installed in your system! The correct driver version will be automatically installed, or loaded from the cache if present (default location is home/.wdm).

**2) EMADB setup:** allows running some options command such as **install project packages** to run the developer model project installation, and **remove logs** to remove all logs saved in `resources/logs`. 

**3) Exit and close** 


### 3.2 Resources
This folder is used to organize the main data for the project, including downloaded files (saved in `resources/download`) and the app logs (`resources/logs`). The `resources/drugs.txt` file contains the names of the drugs you want to download the reports for.  

### 4. Configurations
For customization, you can modify the main configuration parameters using `settings/app_configurations.json` 

#### General Configuration

| Setting                | Description                                                    |
|------------------------|----------------------------------------------------------------|
| IGNORE_SSL_ERROR       | Ignore SSL error during connection                             |
| HEADLESS               | Use webdriver without GUI                                      |
| WAIT_TIME              | Waiting time before considering action failed                  |

## 5. License
This project is licensed under the terms of the MIT license. See the LICENSE file for details.

