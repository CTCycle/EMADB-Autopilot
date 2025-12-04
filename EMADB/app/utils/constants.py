from os.path import abspath, join

# [FOLDER PATHS]
###############################################################################
ROOT_DIR = abspath(join(__file__, "../../../.."))
PROJECT_DIR = join(ROOT_DIR, "EMADB")
SETUP_PATH = join(ROOT_DIR, "setup")
RESOURCES_PATH = join(PROJECT_DIR, "resources")
DOWNLOAD_PATH = join(RESOURCES_PATH, "download")
CONFIG_PATH = join(RESOURCES_PATH, "configurations")
LOGS_PATH = join(RESOURCES_PATH, "logs")

# [UI LAYOUT PATH]
###############################################################################
UI_PATH = join(PROJECT_DIR, "app", "layout", "main_window.ui")
