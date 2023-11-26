# EMADB Autopilot

## Project description
This project is aimed at developing a script to autonomously navigate the EMA database of EudraVigilance (European Database of suspected adverse drug reactions reports). EudraVigilance is a data processing network and management system for reporting and evaluating suspected adverse drug reactions (ADRs) during the development, and following the marketing authorization of medicinal products in the European Economic Area (EEA). The system supports the electronic exchange of suspected adverse drug reaction reports known as Individual Case Safety Reports (ICSRs) between the European Medicines Agency (EMA), National Competent Authorities (NCAs), Marketing Authorization Holders (MAHs), and sponsors of clinical trials in the EEA. 

This automated system will navigate to https://www.adrreports.eu/en/search.html and look for target drugs (from the source .csv file containing a list of drug names), to then extract data reports in the form of excel files. The script is based on chromedriver, meaning that it will simulate a user interacting with a browser to navigate the online database. 

## How to use
Run the main file EMADB_launcher.py to start the automated browser. The drugs_dataset.csv file in the dataset folder must contain the list of drug names which interactions needed to be checked. Once the scraper has finished its job, you will find the download excel files in the default download folder (as per chrome browser configuration)

### Requirements
This application has been developed and tested using the following dependencies (Python 3.10.12):

- `art==6.1`
- `pandas==2.0.3`
- `selenium==4.11.2`
- `webdriver-manager==4.0.1`

These dependencies are specified in the provided `requirements.txt` file to ensure full compatibility with the application. 


