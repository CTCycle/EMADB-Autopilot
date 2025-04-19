

###############################################################################
class Configurations:
    
    def __init__(self):
        self.configurations = {'headless' : False,
                               'ignore_SSL' : False,
                               'wait_time' : False} 

    #--------------------------------------------------------------------------  
    def get_configurations(self):
        return self.configurations
    
    #--------------------------------------------------------------------------
    def update_value(self, key: str, value: bool):       
        self.configurations[key] = value