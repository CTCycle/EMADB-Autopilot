import os

from EMADB.commons.utils.scraper.driver import WebDriverToolkit
from EMADB.commons.utils.scraper.autopilot import EMAWebPilot
from EMADB.commons.utils.components import file_remover, drug_to_letter_aggregator
from EMADB.commons.constants import DATA_PATH
from EMADB.commons.logger import logger


# [MAIN WINDOW]
###############################################################################
class SearchEvents:

    def __init__(self, configurations):
        self.configurations = configurations       
        self.headless = configurations.get('headless', False)
        self.ignore_SSL = configurations.get('ignore_SSL', False)
        self.wait_time = configurations.get('wait_time', 0)        

    #--------------------------------------------------------------------------
    def get_drug_names(self):         
        filepath = os.path.join(DATA_PATH, 'drugs_to_search.txt')  
        with open(filepath, 'r') as file:
            drug_list = [x.lower().strip() for x in file.readlines()]

        return drug_list  

    #--------------------------------------------------------------------------
    def search_using_webdriver(self, drug_list=None):
        # initialize webdriver and webscraper
        self.toolkit = WebDriverToolkit(self.headless, self.ignore_SSL) 
        webdriver = self.toolkit.initialize_webdriver()
        webscraper = EMAWebPilot(webdriver, self.wait_time)  
        # check if files downloaded in the past are still present, then remove them
        # create a dictionary of drug names with their initial letter as key    
        file_remover()
        if drug_list is None:
            drug_list = self.get_drug_names()

        grouped_drugs = drug_to_letter_aggregator(drug_list)
        # click on letter page (based on first letter of names group) and then iterate over
        # all drugs in that page (from the list). Download excel reports and rename them automatically         
        webscraper.download_manager(grouped_drugs) 

