from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

from EMADB.commons.constants import CONFIG, DOWNLOAD_PATH
from EMADB.commons.logger import logger


# [WEBDRIVER]
###############################################################################
class WebDriverToolkit:    
    
    def __init__(self, check_version=False):        
           
        self.options = webdriver.ChromeOptions()
        
        if CONFIG["HEADLESS"]:
            self.options.add_argument('--headless')       
        if CONFIG["IGNORE_SSL_ERROR"]:
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
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument("--disable-search-engine-choice-screen")
        
        if check_version:
            # Check for ChromeDriver installation
            if not self.is_chromedriver_installed():
                logger.error('ChromeDriver is not installed or not in the system path.')        
            # Check Chrome version compatibility
            if not self.check_chrome_version():
                logger.error('Chrome version is not compatible with ChromeDriver.')

    #--------------------------------------------------------------------------
    def is_chromedriver_installed(self):

        '''
        This method checks if the Chrome WebDriver is installed and can be initialized.
        It attempts to create and quit a WebDriver instance and logs any error encountered.

        Keywords arguments:
            None

        Returns:
            bool: True if Chrome WebDriver is successfully initialized, otherwise False.

    '''
        try:
            driver = webdriver.Chrome(options=self.options)
            driver.quit()
            return True
        except Exception as e:
            logger.error(f'Error initializing ChromeDriver: {e}')
            return False

    #--------------------------------------------------------------------------
    def check_chrome_version(self):

        '''
        Initializes a Chrome WebDriver instance to check the current version of Chrome installed.
        It logs the detected version or any error encountered during the process.

        Keywords arguments:
            None

        Returns:
            bool: True if the Chrome version is successfully detected, otherwise False.

        '''        
        try:
            driver = webdriver.Chrome(options=self.options)
            version = driver.capabilities['browserVersion']
            driver.quit()
            logger.info(f'Detected Chrome version: {version}')            
            return True
        except Exception as e:
            logger.error(f'Error detecting Chrome version: {e}')
            return False

    #--------------------------------------------------------------------------
    def initialize_webdriver(self): 

        '''
        Downloads and installs the Chrome WebDriver executable if needed, 
        creates a WebDriver service, and initializes a Chrome WebDriver instance
        with the specified options.

        Keywords arguments:
            None

        Returns:
            driver: A Chrome WebDriver instance.

        '''   
        self.path = ChromeDriverManager().install()          
        driver = webdriver.Chrome(options=self.options)                   
        
        return driver
    
     
