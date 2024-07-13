import json
from os.path import join, dirname, abspath 

PROJECT_DIR = dirname(dirname(abspath(__file__)))
DATA_PATH = join(PROJECT_DIR, 'resources')
DOWNLOAD_PATH = join(DATA_PATH, 'download')
LOGS_PATH = join(PROJECT_DIR, 'resources', 'logs')

CONFIG_PATH = join(PROJECT_DIR, 'configurations.json')
with open(CONFIG_PATH, 'r') as file:
    CONFIG = json.load(file)