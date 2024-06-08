import os
from collections import defaultdict

# [SETTING WARNINGS]
import warnings
warnings.simplefilter(action='ignore', category = Warning)

# [IMPORT CUSTOM MODULES]
from commons.utils.datascraper import WebDriverToolkit, EMAScraper
from commons.pathfinder import DATA_PATH
import commons.configurations as cnf

# [RUN MAIN]
if __name__ == '__main__':

    # 1. [INITIALIZE WEBDRIVER]
    #--------------------------------------------------------------------------
    # activate chromedriver and scraper        
    WD_toolkit = WebDriverToolkit(DATA_PATH, headless=cnf.HEADLESS)
    webdriver = WD_toolkit.initialize_webdriver()

    # 2. [LOAD AND PREPARE DATA]
    #--------------------------------------------------------------------------
    # check if files downloaded in the past are still present, then remove them    
    xlsx_files = [x for x in os.listdir(DATA_PATH) if x.endswith('.xlsx')]
    for filename in xlsx_files:
        file_path = os.path.join(DATA_PATH, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)

    # load drug names    
    filepath = os.path.join(DATA_PATH, 'drugs.txt')  
    with open(filepath, 'r') as file:
        drug_list = [x.lower().strip() for x in file.readlines()]             

    # get list of drugs and group them by initial letter    
    unique_drug_names = sorted(list(set(drug_list)))
    grouped_drugs = defaultdict(list)
    for drug in unique_drug_names:    
        grouped_drugs[drug[0]].append(drug)
    grouped_drugs = dict(grouped_drugs)

    # click on letter page (based on first letter of names group) and then iterate over
    # all drugs in that page (from the list). download excel reports and rename them automatically    
    webscraper = EMAScraper(webdriver)   
    for letter, drugs in grouped_drugs.items():    
        webdriver.get(webscraper.data_URL)       
        letter_css = f"a[onclick=\"showSubstanceTable('{letter.lower()}')\"]"   
        webscraper.autoclick(10, letter_css, mode='CSS')
        for d in drugs:        
            print(f'Collecting data for drug: {d}')
            try:
                placeholder = webscraper.drug_finder(10, d)             
                excel_ph = webscraper.excel_downloader(10, DATA_PATH)            
                DAP_path = os.path.join(DATA_PATH, 'DAP.xlsx')
                rename_path = os.path.join(DATA_PATH, f'{d}.xlsx')
                os.rename(DAP_path, rename_path)             
            except:
                print(f'An error has been encountered while fetching {d} data. Skipping this drug...')




