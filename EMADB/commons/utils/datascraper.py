import os
import time
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from EMADB.commons.constants import CONFIG, DOWNLOAD_PATH, DATA_PATH
from EMADB.commons.logger import logger


# [WEBDRIVER]
###############################################################################
class WebDriverToolkit:    
    
    def __init__(self):        
           
        self.option = webdriver.ChromeOptions()        
        if CONFIG["HEADLESS"]:
            self.option.add_argument('--headless')
        if CONFIG["IGNORE_SSL_ERROR"]: 
            self.option.add_argument('--ignore-ssl-errors=yes')
            self.option.add_argument('--ignore-certificate-errors')       
        self.chrome_prefs = {'download.default_directory' : DOWNLOAD_PATH}
        self.option.experimental_options['prefs'] = self.chrome_prefs
        self.chrome_prefs['profile.default_content_settings'] = {'images': 2}
        self.chrome_prefs['profile.managed_default_content_settings'] = {'images': 2}

    #--------------------------------------------------------------------------
    def initialize_webdriver(self): 

        '''
        This method downloads and installs the Chrome WebDriver executable if needed, 
        creates a WebDriver service, and initializes a Chrome WebDriver instance
        with the specified options.

        Returns:
            driver: A Chrome WebDriver instance.

        '''   
        self.path = ChromeDriverManager().install()    
        # Check if the WebDriver is already cached
        if os.path.exists(self.path):
            logger.debug(f'WebDriver is already cached in {self.path}')
        else:
            logger.debug(f'Downloading and installing WebDriver in {self.path}')
        
        self.service = Service(executable_path=self.path)
        driver = webdriver.Chrome(service=self.service, options=self.option)                   
        
        return driver
    
     
# [SCRAPER]
###############################################################################
class EMAScraper: 

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
    def excel_downloader(self, download_path):

        '''
        Download an Excel file from a web page and wait for the file to appear 
        in the specified download path.

        Keyword Arguments:
            wait_time (int): The maximum time (in seconds) to wait for elements to appear and for the download to complete.
            download_path (str): The path where the downloaded file should be saved.

        Returns:
            item: The WebElement representing the last clicked item.

        '''  
        wait = WebDriverWait(self.driver, self.wait_time)
        XPATH = '//*[@id="uberBar_dashboardpageoptions_image"]'       
        item = wait.until(EC.visibility_of_element_located((By.XPATH, XPATH)))
        item.click()        
        XPATH = '//*[@id="idPageExportToExcel"]/table/tbody/tr/td[2]'
        item = wait.until(EC.visibility_of_element_located((By.XPATH, XPATH)))
        item.click()        
        XPATH = '//*[@id="idDashboardExportToExcelMenu"]/table/tbody/tr[1]/td[1]/a[2]/table/tbody/tr/td[2]'
        item = wait.until(EC.visibility_of_element_located((By.XPATH, XPATH)))
        item.click()         
        while True:
            current_files = os.listdir(download_path)
            if 'DAP.xlsx' in current_files:
                break
            else:
                time.sleep(0.5)
                continue        
        self.driver.switch_to.window(self.driver.window_handles[1])     
        self.driver.close()        
        self.driver.switch_to.window(self.driver.window_handles[0])
        
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
                    self.excel_downloader(DOWNLOAD_PATH)            
                    DAP_path = os.path.join(DOWNLOAD_PATH, 'DAP.xlsx')
                    rename_path = os.path.join(DOWNLOAD_PATH, f'{d}.xlsx')
                    os.rename(DAP_path, rename_path) 
                    logger.debug(f'Succesfully downloaded file {rename_path}')            
                except:
                    logger.error(f'An error has been encountered while fetching {d} data. Skipping this drug.')
                    

        


    
 
            