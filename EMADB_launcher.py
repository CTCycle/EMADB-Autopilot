import os
import art
from collections import defaultdict

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

# activate chromedriver and scraper
#------------------------------------------------------------------------------
modules_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'modules')
WD_toolkit = WebDriverToolkit(modules_path, GlobVar.data_path, headless=cnf.headless)
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

# click on letter page (based on first letter of names group) and then iterate over
# all drugs in that page (from the list). download excel reports and rename them automatically
#------------------------------------------------------------------------------
webscraper = EMAScraper(webdriver)
for letter, drugs in grouped_drugs.items():         
    letter_css = f"a[onclick=\"showSubstanceTable('{letter.lower()}')\"]"   
    webscraper.autoclick(20, letter_css, mode='CSS')
    for d in drugs:
        print(f'Collecting data for drug: {d}')
        try:
            placeholder = webscraper.drug_finder(30, d)             
            excel_ph = webscraper.excel_downloader(30, GlobVar.data_path)            
            DAP_path = os.path.join(GlobVar.data_path, 'DAP.xlsx')
            rename_path = os.path.join(GlobVar.data_path, f'{d}.xlsx')
            os.rename(DAP_path, rename_path)             
        except:
            print(f'An error has been encountered while fetching {d} data. Skipping this drug...')



