import pyderman as driver 
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time

url = 'https://www.boxofficemojo.com/year/?area=ES'
FILE_DIR='/home/vicente/tmp/chromedriver/'

def install_browser(file_dir):

    path = driver.install(browser=driver.chrome,
      file_directory=file_dir,
      chmod=True,
      overwrite=False,
      verbose=True,
      version=None,
      filename='chromedriver')
    print('Installed chromedriver to path: %s' % path)

def setup_chrome(file_dir):

    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certification-errors')
    options.add_argument('--incognito')
    # options.add_argument('--headless')
    
    driver = webdriver.Chrome(file_dir + 'chromedriver',
        options=options)
    
    return driver

def loop_table(driver):

    anchors_len = len(driver.find_elements(By.XPATH, "//a[contains(@href, 'year')]"))
    for i in range(anchors_len):
          anchor = driver.find_elements(By.XPATH, "//a[contains(@href, 'year')]")[i]
          if (anchor.text.isdigit()):
              anchor.click()
              time.sleep(2)
              visit_movies(driver)
              driver.back()

def visit_movies(driver):

    anchors_len = len(driver.find_elements(By.XPATH, "//a[contains(@href, 'release') and contains(@class, 'a-link-normal') and not(contains(@href, 'imdb'))]"))
    for i in range(anchors_len):
        anchor = driver.find_elements(By.XPATH, "//a[contains(@href, 'release') and contains(@class, 'a-link-normal') and not(contains(@href, 'imdb'))]")[i]
        if (anchor.text in ['Release Date', '']):
            continue
        anchor.click()
        time.sleep(3)
        driver.back()
        if (i > 2):
            break

if __name__ == '__main__':
    install_browser(FILE_DIR)
    driver = setup_chrome(FILE_DIR)
 
    driver.get(url)
    loop_table(driver)

#     page_source = driver.page_source

#     soup = BeautifulSoup(page_source, features='html.parser')
# 
#     table_container = soup.find('div', {'id': 'table'})
# 
#     my_tables = table_container.find('table', {'class': 'scrolling-data-table'})
#     for my_table in my_tables:
#       for row in my_table.find_all('tr'):
#         current_year = row.find('td')
#         
# 
#         print(row.get_text())

