# EMADB AutoPilot

## 1. Project Overview
This project is aimed at developing a script to autonomously navigate the EMA database of EudraVigilance (European Database of suspected adverse drug reactions reports). EudraVigilance is a data processing network and management system for reporting and evaluating suspected adverse drug reactions (ADRs) during the development, and following the marketing authorization of medicinal products in the European Economic Area (EEA). The system supports the electronic exchange of suspected adverse drug reaction reports known as Individual Case Safety Reports (ICSRs) between the European Medicines Agency (EMA), National Competent Authorities (NCAs), Marketing Authorization Holders (MAHs), and sponsors of clinical trials in the EEA. 

This automated system will navigate to https://www.adrreports.eu/en/search.html and look for target drugs, which are found by looking at drugs name in a .txt file within the data folder (the file can have any name). Then, it downloads data reports in the form of excel files. The script is based on chromedriver, meaning that it will simulate a user interacting with a browser to navigate the online database. 

## 2. Installation 
The installation process is designed for simplicity, using .bat scripts to automatically create a virtual environment with all necessary dependencies. Please ensure that Anaconda or Miniconda is properly installed on your system before proceeding.

- The `scripts/environment_setup.bat` file offers a convenient one-click solution to set up your virtual environment.
- **IMPORTANT:** run `scripts/package_setup.bat` if the path to the project folder is changed for any reason after installation, or the app won't work! 

## 3. How to use
Within the main project folder (EMABD) you will find other folders, each designated to specific tasks. Run the main file `EMAutoPilot.py` to start the automated browser. Since the script is based on Chromedriver, your need to have Google Chrome browser installed in your system! The correct driver version will be automatically installed, or loaded from the cache if present (default location is home/.wdm).

### Resources
This folder is used to organize the main data for the project, including downloaded files (saved in `resources/download`) and the app logs (`resources/logs`). The `resources/drugs.txt` file contains the names of the drugs you want to download the reports for.  

### 3.1 Configurations
For customization, you can modify the main configuration parameters using `settings/configurations.json`  

| Setting                | Description                                                    |
|------------------------|----------------------------------------------------------------|
| SEED                   | Random seed                                                    |
| IGNORE_SSL_ERROR       | Ignore SSL error during connection                             |
| HEADLESS               | Use webdriver without GUI                                      |
| WAIT_TIME              | Waiting time before considering action failed                  |

## License
This project is licensed under the terms of the MIT license. See the LICENSE file for details.

