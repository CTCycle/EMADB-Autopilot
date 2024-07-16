# [SETTING WARNINGS]
import warnings
warnings.simplefilter(action='ignore', category=Warning)

# [IMPORT CUSTOM MODULES]
from EMADB.commons.utils.datascraper import WebDriverToolkit, EMAScraper
from EMADB.commons.utils.components import file_remover, drug_to_letter_aggregator


# [RUN MAIN]
###############################################################################
if __name__ == '__main__':

    # 1. [INITIALIZE WEBDRIVER]
    #--------------------------------------------------------------------------
    # activate chromedriver and scraper        
    WD_toolkit = WebDriverToolkit()
    webdriver = WD_toolkit.initialize_webdriver()

    # 2. [LOAD AND PREPARE DATA]
    #--------------------------------------------------------------------------
    # check if files downloaded in the past are still present, then remove them
    # create a dictionary of drug names with their initial letter as key    
    file_remover()    
    grouped_drugs = drug_to_letter_aggregator()

    # click on letter page (based on first letter of names group) and then iterate over
    # all drugs in that page (from the list). Download excel reports and rename them automatically    
    webscraper = EMAScraper(webdriver)   
    webscraper.download_manager(grouped_drugs)




