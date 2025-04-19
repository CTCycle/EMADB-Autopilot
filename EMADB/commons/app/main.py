# [SETTING WARNINGS]
import warnings
warnings.simplefilter(action='ignore', category=Warning)

# [IMPORT CUSTOM MODULES]
from EMADB.commons.interface.window import MainWindow
from EMADB.commons.constants import UI_PATH
from EMADB.commons.logger import logger


# [RUN MAIN]
###############################################################################
if __name__ == "__main__":       
    manager = MainWindow()   
    manager.run()

   
