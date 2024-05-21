import os
import time
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# [WEBDRIVER]
#==============================================================================
class WebDriverToolkit:    
    
    def __init__(self, download_path, headless=True):        
        self.download_path = download_path      
        self.option = webdriver.ChromeOptions()
        if headless==True:
            self.option.add_argument('--headless')        
        self.chrome_prefs = {'download.default_directory' : download_path}
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
        self.service = Service(executable_path=self.path)
        driver = webdriver.Chrome(service=self.service, options=self.option)                   
        
        return driver 
    
# [SCRAPER]
#==============================================================================
class EMAScraper: 

    def __init__(self, driver):         
        self.driver = driver
        self.data_URL = 'https://www.adrreports.eu/en/search_subst.html'
        self.alphabet = []          
               
    #--------------------------------------------------------------------------
    def autoclick(self, wait_time, string, mode='XPATH'):  

        '''
        Automatically click an element based on a provided XPath or CSS selector.

        Keyword Arguments:
            wait_time (int): The maximum time (in seconds) to wait for the element to appear.
            string (str): The XPath or CSS selector string to locate the element.
            mode (str, optional): The mode of selection, either 'XPATH' (default) or 'CSS'.

        Returns:
            None
        '''
        wait = WebDriverWait(self.driver, wait_time)     
        if mode=='XPATH':
            item = wait.until(EC.visibility_of_element_located((By.XPATH, string)))
            item.click()
        elif mode=='CSS':
            item = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, string)))
            item.click()    
    
    #--------------------------------------------------------------------------
    def drug_finder(self, wait_time, name):

        '''
        Find and click on a drug link by searching for its name.

        Keyword Arguments:
            wait_time (int): The maximum time (in seconds) to wait for the drug link to appear.
            name (str): The name of the drug to search for.

        Returns:
            item: The WebElement representing the drug link that was clicked.

        '''  
        wait = WebDriverWait(self.driver, wait_time)
        cap_name = name.upper()               
        item = wait.until(EC.visibility_of_element_located((By.PARTIAL_LINK_TEXT, cap_name)))
        item.click()
        original_window = self.driver.current_window_handle
        WebDriverWait(self.driver, 10).until(EC.number_of_windows_to_be(2)) 
        self.driver.switch_to.window(self.driver.window_handles[1])       

        return item   
    
    #--------------------------------------------------------------------------
    def excel_downloader(self, wait_time, download_path):

        '''
        Download an Excel file from a web page and wait for the file to appear 
        in the specified download path.

        Keyword Arguments:
            wait_time (int): The maximum time (in seconds) to wait for elements to appear and for the download to complete.
            download_path (str): The path where the downloaded file should be saved.

        Returns:
            item: The WebElement representing the last clicked item.

        '''  
        wait = WebDriverWait(self.driver, wait_time)
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

        return item   
    
 
            