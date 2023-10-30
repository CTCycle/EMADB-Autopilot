import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re



# define the class for inspection of the input folder and generation of files list.
#==============================================================================
#==============================================================================
#==============================================================================
class WebDriverToolkit:
    
    """
    Initializes a webdriver instance with Chrome options set to disable images loading.
    
    Keyword arguments:
    
    wd_path (str): The file path to the Chrome webdriver executable
    
    Returns:
        
    None 
    
    """
    def __init__(self, path):
        self.path = os.path.join(path, 'chromedriver.exe')       
        self.option = webdriver.ChromeOptions()
        self.service = Service(executable_path=self.path)
        self.chrome_prefs = {}
        self.option.experimental_options['prefs'] = self.chrome_prefs
        self.chrome_prefs['profile.default_content_settings'] = {'images': 2}
        self.chrome_prefs['profile.managed_default_content_settings'] = {'images': 2} 

    def initialize_webdriver(self):
        driver = webdriver.Chrome(service=self.service, options=self.option) 
        
        return driver
   


    
# define the class for inspection of the input folder and generation of files list
#==============================================================================
#==============================================================================
#==============================================================================
class EMAScraper: 

    def __init__(self, driver):         
        self.driver = driver
        self.data_URL = 'https://www.adrreports.eu/en/search.html'
        self.driver.get(self.data_URL)
               
    #==========================================================================
    def autoclick(self, time, xpath):  
        wait = WebDriverWait(self.driver, time)        
        item = wait.until(EC.visibility_of_element_located((By.XPATH, xpath)))
        item.click()        

        return item
    
    #==========================================================================
    def drug_finder(self, time, name):  
        wait = WebDriverWait(self.driver, time)
        cap_name = name.upper()               
        item = wait.until(EC.visibility_of_element_located((By.PARTIAL_LINK_TEXT, cap_name)))
        item.click()        

        return item
    
    #==========================================================================
    def excel_downloader(self, time):  
        wait = WebDriverWait(self.driver, time)
        XPATH = '//*[@id="uberBar_dashboardpageoptions_image"]'       
        item = wait.until(EC.visibility_of_element_located((By.XPATH, XPATH)))
        item.click()
        wait = WebDriverWait(self.driver, 10)
        XPATH = '//*[@id="idPageExportToExcel"]/table/tbody/tr/td[2]'
        item = wait.until(EC.visibility_of_element_located((By.XPATH, XPATH)))
        item.click() 
        wait = WebDriverWait(self.driver, 10)  
        XPATH = '//*[@id="idDashboardExportToExcelMenu"]/table/tbody/tr[1]/td[1]/a[1]/table/tbody/tr/td[2]'
        item = wait.until(EC.visibility_of_element_located((By.XPATH, XPATH)))
        item.click() 
        self.driver.refresh()

        return item
    
    #==========================================================================
    def excel_downloader(self, time):  
        wait = WebDriverWait(self.driver, time)
        XPATH = '//*[@id="uberBar_dashboardpageoptions_image"]'       
        item = wait.until(EC.visibility_of_element_located((By.XPATH, XPATH)))
        item.click()
        wait = WebDriverWait(self.driver, 10)
        XPATH = '//*[@id="idPageExportToExcel"]/table/tbody/tr/td[2]'
        item = wait.until(EC.visibility_of_element_located((By.XPATH, XPATH)))
        item.click() 
        wait = WebDriverWait(self.driver, 10)  
        XPATH = '//*[@id="idDashboardExportToExcelMenu"]/table/tbody/tr[1]/td[1]/a[1]/table/tbody/tr/td[2]'
        item = wait.until(EC.visibility_of_element_located((By.XPATH, XPATH)))
        item.click() 
        self.driver.refresh()

        return item   
    
 
            