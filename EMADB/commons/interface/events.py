import os

from EMADB.commons.utils.driver.toolkit import WebDriverToolkit
from EMADB.commons.utils.driver.autopilot import EMAWebPilot
from EMADB.commons.interface.workers import check_thread_status
from EMADB.commons.utils.components import file_remover, drug_to_letter_aggregator
from EMADB.commons.constants import DATA_PATH
from EMADB.commons.logger import logger



###############################################################################
class SearchEvents:

    def __init__(self, configuration):
        self.configuration = configuration       
        self.headless = configuration.get('headless', False)
        self.ignore_SSL = configuration.get('ignore_SSL', False)
        self.wait_time = configuration.get('wait_time', 0)        

    #--------------------------------------------------------------------------
    def get_drugs_from_file(self):         
        filepath = os.path.join(DATA_PATH, 'drugs_to_search.txt')  
        with open(filepath, 'r') as file:
            drug_list = [x.lower().strip() for x in file.readlines()]

        return drug_list  

    #--------------------------------------------------------------------------
    def search_using_webdriver(self, drug_list=None, worker=None):        
        # check if files downloaded in the past are still present, then remove them
        # create a dictionary of drug names with their initial letter as key    
        file_remover()
        if drug_list is None:
            logger.info('No drug targets provided, reading from source file directly')
            drug_list = self.get_drugs_from_file()

        # initialize webdriver and webscraper
        self.toolkit = WebDriverToolkit(self.headless, self.ignore_SSL) 
        webdriver = self.toolkit.initialize_webdriver()
        
        # check for thread status and eventually stop it  
        check_thread_status(worker)        
        # click on letter page (based on first letter of names group) and then iterate over
        # all drugs in that page (from the list). Download excel reports and rename them automatically 
        grouped_drugs = drug_to_letter_aggregator(drug_list)  

        webscraper = EMAWebPilot(webdriver, self.wait_time)      
        webscraper.download_manager(grouped_drugs, worker=worker) 

    