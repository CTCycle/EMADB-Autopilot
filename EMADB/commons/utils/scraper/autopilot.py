import os
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from EMADB.commons.interface.workers import check_thread_status
from EMADB.commons.constants import DOWNLOAD_PATH
from EMADB.commons.logger import logger

    
# [SCRAPER]
###############################################################################
class EMAWebPilot: 

    def __init__(self, driver, wait_time=10):         
        self.driver = driver
        self.wait_time = wait_time
        self.data_URL = 'https://www.adrreports.eu/en/search_subst.html'
        self.alphabet = []          
               
    #--------------------------------------------------------------------------
    def autoclick(self, string, mode='XPATH'):  
        wait = WebDriverWait(self.driver, self.wait_time) 
        modes = {'XPATH': wait.until(EC.visibility_of_element_located((By.XPATH, string))),
                 'CSS': wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, string)))}    
              
        modes[mode].click() 
    
    #--------------------------------------------------------------------------
    def drug_finder(self, name):
        wait = WebDriverWait(self.driver, self.wait_time)                       
        item = wait.until(EC.visibility_of_element_located((By.PARTIAL_LINK_TEXT, name.upper())))
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
    def download_manager(self, grouped_drugs, **kwargs):
        for letter, drugs in grouped_drugs.items():    
            self.driver.get(self.data_URL)       
            letter_css = f"a[onclick=\"showSubstanceTable('{letter.lower()}')\"]"   
            self.autoclick(letter_css, mode='CSS')
            for d in drugs:
                # check for thread status and eventually stop it 
                check_thread_status(kwargs.get('worker', None))         
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

 
                          


    
 
            