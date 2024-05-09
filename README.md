# EMADB Autopilot

## 1. Project Overview
This project is aimed at developing a script to autonomously navigate the EMA database of EudraVigilance (European Database of suspected adverse drug reactions reports). EudraVigilance is a data processing network and management system for reporting and evaluating suspected adverse drug reactions (ADRs) during the development, and following the marketing authorization of medicinal products in the European Economic Area (EEA). The system supports the electronic exchange of suspected adverse drug reaction reports known as Individual Case Safety Reports (ICSRs) between the European Medicines Agency (EMA), National Competent Authorities (NCAs), Marketing Authorization Holders (MAHs), and sponsors of clinical trials in the EEA. 

This automated system will navigate to https://www.adrreports.eu/en/search.html and look for target drugs, which are found by looking at drugs name in a .txt file within the data folder (the file can have any name). Then, it downloads data reports in the form of excel files. The script is based on chromedriver, meaning that it will simulate a user interacting with a browser to navigate the online database. 

## 2. Installation 
The installation process is designed for simplicity, using .bat scripts to automatically create a virtual environment with all necessary dependencies. Please ensure that Anaconda or Miniconda is installed on your system before proceeding.

- The `create_environment.bat` file, located in the scripts folder, offers a convenient one-click solution to set up your virtual environment.

## 3. How to use
Run the main file EMADBAP.py to start the automated browser. The drugs_dataset.csv file in the dataset folder will be used as reference to get target drug names. Once the webscraper module has finished to run, you will find the download excel files in the default download folder (as per chrome browser configuration).

### 3.1 Configurations
For customization, you can modify the main script parameters via the `configurations.py` file in the main folder. 

| Category                | Setting                | Description                                                    |
|-------------------------|------------------------|----------------------------------------------------------------|
| **General settings**    | HEADLESS               | Use webdriver without GUI                                      |


## License
This project is licensed under the terms of the MIT license. See the LICENSE file for details.


