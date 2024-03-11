import os

# Define paths for the script
#------------------------------------------------------------------------------
data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')

# create folders if they do not exist
#------------------------------------------------------------------------------
os.mkdir(data_path) if not os.path.exists(data_path) else None



