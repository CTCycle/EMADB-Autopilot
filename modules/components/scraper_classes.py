import os
import time
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC




# define the class for inspection of the input folder and generation of files list.
#==============================================================================
#==============================================================================
#==============================================================================
class WebDriverToolkit:    
    
    def __init__(self, driver_path, download_path, headless=True):
        self.driver_path = os.path.join(driver_path, 'chromedriver.exe') 
        self.download_path = download_path      
        self.option = webdriver.ChromeOptions()
        if headless==True:
            self.option.add_argument('--headless')
        self.service = Service(executable_path=self.driver_path)
        self.chrome_prefs = {'download.default_directory' : download_path}
        self.option.experimental_options['prefs'] = self.chrome_prefs
        self.chrome_prefs['profile.default_content_settings'] = {'images': 2}
        self.chrome_prefs['profile.managed_default_content_settings'] = {'images': 2}

    def initialize_webdriver(self):       
        self.path = ChromeDriverManager().install()
        self.service = Service(executable_path=self.path)
        driver = webdriver.Chrome(service=self.service, options=self.option)
        print('The latest ChromeDriver version is now installed in the .wdm folder in user/home')                  
        
        return driver 
   


    
# define the class for inspection of the input folder and generation of files list
#==============================================================================
#==============================================================================
#==============================================================================
class EMAScraper: 

    def __init__(self, driver):         
        self.driver = driver
        self.data_URL = 'https://www.adrreports.eu/en/search_subst.html'
        self.alphabet = []
        self.driver.get(self.data_URL)      
               
    #==========================================================================
    def autoclick(self, wait_time, string, mode='XPATH'):  
        wait = WebDriverWait(self.driver, wait_time)     
        if mode=='XPATH':
            item = wait.until(EC.visibility_of_element_located((By.XPATH, string)))
            item.click()
        elif mode=='CSS':
            item = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, string)))
            item.click()    
    
    #==========================================================================
    def drug_finder(self, wait_time, name):  
        wait = WebDriverWait(self.driver, wait_time)
        cap_name = name.upper()               
        item = wait.until(EC.visibility_of_element_located((By.PARTIAL_LINK_TEXT, cap_name)))
        item.click()
        original_window = self.driver.current_window_handle
        WebDriverWait(self.driver, 10).until(EC.number_of_windows_to_be(2)) 
        self.driver.switch_to.window(self.driver.window_handles[1])       

        return item   
    
    #==========================================================================
    def excel_downloader(self, wait_time, download_path):  
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
    
 
            