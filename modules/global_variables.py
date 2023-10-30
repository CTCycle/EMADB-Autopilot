import os

data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'dataset')

if not os.path.exists(data_path):
    os.mkdir(data_path)

