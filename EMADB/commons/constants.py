from os.path import join, abspath 

# [FOLDER PATHS]
###############################################################################
ROOT_DIR = abspath(join(__file__, "../../.."))
PROJECT_DIR = join(ROOT_DIR, 'EMADB')
SETUP_PATH = join(ROOT_DIR, 'setup')
DATA_PATH = join(PROJECT_DIR, 'resources')
DOWNLOAD_PATH = join(DATA_PATH, 'download')
LOGS_PATH = join(DATA_PATH, 'logs')

# [UI LAYOUT PATH]
###############################################################################
UI_PATH = join(PROJECT_DIR, 'commons', 'interface', 'layout', 'window_layout.ui')

