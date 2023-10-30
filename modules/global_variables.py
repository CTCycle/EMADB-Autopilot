import os

data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
download_path = os.path.join(data_path, 'EMA reports')


if not os.path.exists(data_path):
    os.mkdir(data_path)
if not os.path.exists(download_path):
    os.mkdir(download_path)

