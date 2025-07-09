from selenium.webdriver import Chrome, ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager

from EMADB.app.src.commons.constants import DOWNLOAD_PATH
from EMADB.app.src.commons.logger import logger


# [WEBDRIVER]
###############################################################################
class WebDriverToolkit:    
    
    def __init__(self, headless=False, ignore_SSL=True):          
        self.options = ChromeOptions()                
        if headless:
            self.options.add_argument('--headless')       
        if ignore_SSL:
            self.options.add_argument('--ignore-ssl-errors=yes')
            self.options.add_argument('--ignore-certificate-errors')

        # Set download directory       
        self.chrome_prefs = {'download.default_directory': DOWNLOAD_PATH}        
        # Disable images for smoother performances
        self.chrome_prefs['profile.default_content_settings'] = {'images': 2}
        self.chrome_prefs['profile.managed_default_content_settings'] = {'images': 2}        
        self.options.experimental_options['prefs'] = self.chrome_prefs      

        # Additional recommended options        
        self.options.add_argument('--disable-extensions')        
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument("--disable-search-engine-choice-screen")           
        self.options.add_argument('--disable-gpu')       

    #--------------------------------------------------------------------------
    def is_chromedriver_installed(self):        
        try:
            driver = Chrome(options=self.options)
            driver.quit()
            return 'ChomeDriver is installed'
        except Exception as e:
            logger.error(f'Error initializing ChromeDriver: {e}')
            return f'Error initializing ChromeDriver: {e}'

    #--------------------------------------------------------------------------
    def check_chrome_version(self):  
        try:
            driver = Chrome(options=self.options)
            version = driver.capabilities['browserVersion']
            driver.quit()
            logger.info(f'Detected Chrome version: {version}')            
            return version
        except Exception as e:
            logger.error(f'Error detecting Chrome version: {e}')
            return 'Version not detected'

    #--------------------------------------------------------------------------
    def initialize_webdriver(self):         
        self.path = ChromeDriverManager().install()          
        driver = Chrome(options=self.options)                   
        
        return driver
    
     
