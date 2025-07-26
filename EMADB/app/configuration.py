import os
import json

from EMADB.app.constants import CONFIG_PATH

###############################################################################
class Configuration:
    
    def __init__(self):
        self.configuration = {'headless' : False,
                              'ignore_SSL' : False,
                              'wait_time' : 5.0} 

    #--------------------------------------------------------------------------  
    def get_configuration(self):
        return self.configuration
    
    #--------------------------------------------------------------------------
    def update_value(self, key: str, value: bool):       
        self.configuration[key] = value

    #--------------------------------------------------------------------------
    def save_configuration_to_json(self, name : str):  
        full_path = os.path.join(CONFIG_PATH, f'{name}.json')      
        with open(full_path, 'w') as f:
            json.dump(self.configuration, f, indent=4)