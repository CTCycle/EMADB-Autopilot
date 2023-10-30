import os
import re
import art
import pandas as pd
from collections import defaultdict
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType

# set warnings
#------------------------------------------------------------------------------
import warnings
warnings.simplefilter(action='ignore', category = Warning)

# import modules and classes
#------------------------------------------------------------------------------
from modules.components.scraper_classes import WebDriverToolkit, EMAScraper
import modules.global_variables as GlobVar
import modules.configurations as cnf

# welcome message
#------------------------------------------------------------------------------
ascii_art = art.text2art('EMA AutoPilot')
print(ascii_art)

# [ACTIVATE CHROMEDRIVER VERSION]
#==============================================================================
# ...
#==============================================================================
print('''
Activating chromedriver. Check version for compatibility with the program
      
''')

# check if chromedriver is present
#------------------------------------------------------------------------------
modules_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'modules')
if cnf.check_CD_version == True:
    chromedriver_check = False    
    for file_name in os.listdir(modules_path):            
        if 'chromedriver' in file_name:
            chromedriver_check = True
    if chromedriver_check == False:
        version = os.popen('google-chrome --version').read() 
        version_number = re.search(r'\d+', version).group(0)
        driver_path = ChromeDriverManager(version=version, chrome_type=ChromeType.GOOGLE).install()

# activate chromedriver
#------------------------------------------------------------------------------
WD_toolkit = WebDriverToolkit(modules_path, GlobVar.download_path)
webdriver = WD_toolkit.initialize_webdriver()

# [LOAD AND PREPARE DATA]
#==============================================================================
# Load patient dataset and dictionaries from .csv files in the dataset folder.
# Also, create a clean version of the exploded dataset to work on
#==============================================================================

# activate chromedriver
#------------------------------------------------------------------------------
filepath = os.path.join(GlobVar.data_path, 'drugs_list.txt')  
with open(filepath, 'r') as file:
    drug_list = [x.lower().strip() for x in file.readlines()]             

# get list of drugs and group them by initial letter
#------------------------------------------------------------------------------
unique_drug_names = sorted(list(set(drug_list)))
grouped_drugs = defaultdict(list)
for drug in unique_drug_names:    
    grouped_drugs[drug[0]].append(drug)
grouped_drugs = dict(grouped_drugs)

# open disclaimer page and click on accept
#------------------------------------------------------------------------------
webscraper = EMAScraper(webdriver)
disclaimer_xpath = '//*[@id="container"]/div[4]/form/input[1]'
webscraper.autoclick(30, disclaimer_xpath)

# click on letter page (based on first letter of names group) and then iterate over
# all drugs in that page (from the list). download excel reports and rename them automatically
#------------------------------------------------------------------------------
for letter, drugs in grouped_drugs.items():          
    letter_xpath = f'//a[@onclick="showProductTable(\'{letter.lower()}\')"]'
    webscraper.autoclick(20, letter_xpath)
    for d in drugs:
        placeholder = webscraper.drug_finder(30, d) 
        excel_ph = webscraper.excel_downloader(30, GlobVar.download_path) 
        DAP_path = os.path.join(GlobVar.download_path, 'DAP.xlsx')
        rename_path = os.path.join(GlobVar.download_path, f'{d}.xlsx')
        os.rename(DAP_path, rename_path) 


