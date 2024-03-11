# EMADB Autopilot

## Project Overview
This project is aimed at developing a script to autonomously navigate the EMA database of EudraVigilance (European Database of suspected adverse drug reactions reports). EudraVigilance is a data processing network and management system for reporting and evaluating suspected adverse drug reactions (ADRs) during the development, and following the marketing authorization of medicinal products in the European Economic Area (EEA). The system supports the electronic exchange of suspected adverse drug reaction reports known as Individual Case Safety Reports (ICSRs) between the European Medicines Agency (EMA), National Competent Authorities (NCAs), Marketing Authorization Holders (MAHs), and sponsors of clinical trials in the EEA. 

This automated system will navigate to https://www.adrreports.eu/en/search.html and look for target drugs (from the source .csv file containing a list of drug names), to then download data reports in the form of excel files. The script is based on chromedriver, meaning that it will simulate a user interacting with a browser to navigate the online database. 

## Installation 
First, ensure that you have Python 3.10.12 installed on your system. Then, you can easily install the required Python packages using the provided requirements.txt file:

`pip install -r requirements.txt` 

These dependencies are specified in the provided `requirements.txt` file to ensure full compatibility with the application. 

## How to use
Run the main file EMADBAP.py to start the automated browser. The drugs_dataset.csv file in the dataset folder will be used as reference to get target drug names. Once the webscraper module has finished to run, you will find the download excel files in the default download folder (as per chrome browser configuration).

### Configurations
The configurations.py file allows to change the script configuration. The following parameters are available:

- `headless:` use chromedriver in headless mode (no visible GUI)

## License
This project is licensed under the terms of the MIT license. See the LICENSE file for details.


