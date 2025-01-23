import requests
from bs4 import BeautifulSoup

from EMADB.commons.constants import CONFIG, DOWNLOAD_PATH
from EMADB.commons.logger import logger


    
# [SCRAPER]
###############################################################################
class ATCRequests: 

    def __init__(self, configuration): 
        self.base_URL = 'https://atcddd.fhi.no/atc_ddd_index/'
        self.configuration = configuration                 
               
    #--------------------------------------------------------------------------
    def get_single_ATC_code(self, payload): 

        response = requests.post(self.base_URL, data=payload)

        if response.status_code == 200:
            logger.debug(f'Success for request with payload: {payload}')             
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            results_table = soup.find("table")  
            if results_table:
                rows = results_table.find_all("tr")                
             
                atc_dict = {}                
              
                for row in rows:
                    columns = row.find_all("td")  
                    if len(columns) >= 2:  
                        atc_code = columns[0].text.strip() 
                        description = columns[1].text.strip()  
                        atc_dict[atc_code] = description                
            else:
                logger.warning("No results table found in the response.")
        else:
            logger.error(f"Request failed with status code: {response.status_code}")

        return atc_dict

    #--------------------------------------------------------------------------
    def fetch_multiple_ATC_by_name(self, payloads): 
        
        for pl in payloads:

            results = self.get_single_ATC_code(pl)

        return results
