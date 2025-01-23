# [SETTING WARNINGS]
import warnings
warnings.simplefilter(action='ignore', category=Warning)

# [IMPORT CUSTOM MODULES]
from EMADB.commons.utils.requests import ATCRequests
from EMADB.commons.constants import CONFIG


# [RUN MAIN]
###############################################################################
if __name__ == '__main__':

    # 1. [SEND REQUESTS]
    #--------------------------------------------------------------------------
    # activate chromedriver and scraper
    payloads = [
            {"name": "paracetamol", "namesearchtype": "containing"},
            {"name": "ibuprofen", "namesearchtype": "containing"}
        ]
    
    swagger = ATCRequests(CONFIG)
    
    results = swagger.fetch_multiple_ATC_by_name(payloads)   


    pass    
    


