# webdriver settings
#------------------------------------------------------------------------------
headless=False

# optional pathways for the disclaimer page
#------------------------------------------------------------------------------
disclaimer_xpath = '//*[@id="container"]/div[4]/form/input[1]'
disclaimer_css = '''a[onclick="acceptDisclaimer(true, 'search_subst.html')">"'''
base_css_letters = "a[onclick=\"showSubstanceTable('a')\"]" 