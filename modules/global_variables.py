import os

data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
if not os.path.exists(data_path):
    os.mkdir(data_path)


# optional pathways for the disclaimer page
#------------------------------------------------------------------------------
disclaimer_xpath = '//*[@id="container"]/div[4]/form/input[1]'
disclaimer_css = '''a[onclick="acceptDisclaimer(true, 'search_subst.html')">"'''
base_css_letters = "a[onclick=\"showSubstanceTable('a')\"]" 

