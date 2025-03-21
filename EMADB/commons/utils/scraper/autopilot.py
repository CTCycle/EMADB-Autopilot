import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from EMADB.commons.constants import CONFIG, DOWNLOAD_PATH
from EMADB.commons.logger import logger

    
# [SCRAPER]
###############################################################################
class EMAWebPilot: 

    def __init__(self, driver):         
        self.driver = driver
        self.wait_time = CONFIG["WAIT_TIME"]
        self.data_URL = 'https://www.adrreports.eu/en/search_subst.html'
        self.alphabet = []          
               
    #--------------------------------------------------------------------------
    def autoclick(self, string, mode='XPATH'):  

        '''
        Automatically click an element based on a provided XPath or CSS selector.

        Keyword Arguments:
            wait_time (int): The maximum time (in seconds) to wait for the element to appear.
            string (str): The XPath or CSS selector string to locate the element.
            mode (str, optional): The mode of selection, either 'XPATH' (default) or 'CSS'.

        Returns:
            None
        '''
        wait = WebDriverWait(self.driver, self.wait_time)     
        if mode=='XPATH':
            item = wait.until(EC.visibility_of_element_located((By.XPATH, string)))
            item.click()
        elif mode=='CSS':
            item = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, string)))
            item.click()    
    
    #--------------------------------------------------------------------------
    def drug_finder(self, name):

        '''
        Find and click on a drug link by searching for its name.

        Keyword Arguments:
            wait_time (int): The maximum time (in seconds) to wait for the drug link to appear.
            name (str): The name of the drug to search for.

        Returns:
            item: The WebElement representing the drug link that was clicked.

        '''  
        wait = WebDriverWait(self.driver, self.wait_time)
        cap_name = name.upper()               
        item = wait.until(EC.visibility_of_element_located((By.PARTIAL_LINK_TEXT, cap_name)))
        item.click()
        original_window = self.driver.current_window_handle
        WebDriverWait(self.driver, self.wait_time).until(EC.number_of_windows_to_be(2)) 
        self.driver.switch_to.window(self.driver.window_handles[1])  

    #--------------------------------------------------------------------------
    def close_and_switch_window(self):
        self.driver.switch_to.window(self.driver.window_handles[1])     
        self.driver.close()        
        self.driver.switch_to.window(self.driver.window_handles[0])    

    #--------------------------------------------------------------------------
    def click_and_download(self, current_page=True):
        flag = 1 if current_page else 2
        wait = WebDriverWait(self.driver, self.wait_time)
        XPATH = '//*[@id="uberBar_dashboardpageoptions_image"]'       
        item = wait.until(EC.visibility_of_element_located((By.XPATH, XPATH)))
        item.click()        
        XPATH = '//*[@id="idPageExportToExcel"]/table/tbody/tr/td[2]'
        item = wait.until(EC.visibility_of_element_located((By.XPATH, XPATH)))
        item.click()       
        XPATH = f'//*[@id="idDashboardExportToExcelMenu"]/table/tbody/tr[1]/td[1]/a[{flag}]/table/tbody/tr/td[2]'
        item = wait.until(EC.visibility_of_element_located((By.XPATH, XPATH)))
        item.click()       

    #--------------------------------------------------------------------------
    def check_DAP_filenames(self):
        while True:
            current_files = os.listdir(DOWNLOAD_PATH)
            DAP_files = [x for x in current_files if 'DAP' in x]
            if len(DAP_files) > 0:
                break
            else:
                time.sleep(0.5)
                continue 

    #--------------------------------------------------------------------------
    def download_manager(self, grouped_drugs):
        for letter, drugs in grouped_drugs.items():    
            self.driver.get(self.data_URL)       
            letter_css = f"a[onclick=\"showSubstanceTable('{letter.lower()}')\"]"   
            self.autoclick(letter_css, mode='CSS')
            for d in drugs:        
                logger.info(f'Collecting data for drug: {d}')
                try:
                    self.drug_finder(d)             
                    self.click_and_download(current_page=False)
                    self.check_DAP_filenames()
                    self.close_and_switch_window()                        
                    DAP_path = os.path.join(DOWNLOAD_PATH, 'DAP.xlsx')
                    rename_path = os.path.join(DOWNLOAD_PATH, f'{d}.xlsx')
                    os.rename(DAP_path, rename_path) 
                    logger.debug(f'Succesfully downloaded file {rename_path}')            
                except:
                    logger.error(f'An error has been encountered while fetching {d} data. Skipping this drug.')

 
                          


    
 
            