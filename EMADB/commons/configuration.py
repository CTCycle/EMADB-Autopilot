

###############################################################################
class Configuration:
    
    def __init__(self):
        self.configuration = {'headless' : False,
                              'ignore_SSL' : False,
                              'wait_time' : False} 

    #--------------------------------------------------------------------------  
    def get_configuration(self):
        return self.configuration
    
    #--------------------------------------------------------------------------
    def update_value(self, key: str, value: bool):       
        self.configuration[key] = value