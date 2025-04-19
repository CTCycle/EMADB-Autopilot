

from EMADB.commons.utils.scraper.driver import WebDriverToolkit
from EMADB.commons.utils.scraper.autopilot import EMAWebPilot
from EMADB.commons.utils.components import file_remover, drug_to_letter_aggregator
from EMADB.commons.constants import ROOT_DIR, LOGS_PATH, SETUP_PATH
from EMADB.commons.logger import logger


# [MAIN WINDOW]
###############################################################################
class SearchEvents:

    def __init__(self):
        self.toolkit = WebDriverToolkit()

    #--------------------------------------------------------------------------
    def search_from_file(self):         
        webdriver = self.toolkit.initialize_webdriver()
        webscraper = EMAWebPilot(webdriver)  
        # check if files downloaded in the past are still present, then remove them
        # create a dictionary of drug names with their initial letter as key    
        file_remover()    
        grouped_drugs = drug_to_letter_aggregator()
        # click on letter page (based on first letter of names group) and then iterate over
        # all drugs in that page (from the list). Download excel reports and rename them automatically         
        webscraper.download_manager(grouped_drugs)


