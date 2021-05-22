import pyderman as driver 
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time

url = 'https://www.boxofficemojo.com/year/?area=ES'
LIMIT_MOVIES_YEAR = 2
STARTING_YEAR = 2010
ENDING_YEAR = 2013
FILE_DIR = '/home/vicente/tmp/chromedriver/'

def install_browser(file_dir):

    path = driver.install(browser=driver.chrome,
      file_directory=file_dir,
      chmod=True,
      overwrite=False,
      verbose=True,
      version=None,
      filename='chromedriver')

def setup_chrome(file_dir):

    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certification-errors')
    options.add_argument('--incognito')
    # options.add_argument('--headless')
    
    driver = webdriver.Chrome(file_dir + 'chromedriver',
        options=options)
    
    return driver

def loop_table(driver):

    summary = []
    anchors_len = len(driver.find_elements(By.XPATH, "//a[contains(@href, 'year')]"))
    for i in range(anchors_len):
        anchor = driver.find_elements(By.XPATH, "//a[contains(@href, 'year')]")[i]
        if (anchor.text.isdigit()):
            year = anchor.text
            if (int(year) >= STARTING_YEAR and int(year) <= ENDING_YEAR):
                anchor.click()
                time.sleep(2)
                summary = summary + visit_movies(driver,year)
                driver.back()
    f = open('{}_to_{}_top{}.csv'.format(STARTING_YEAR, ENDING_YEAR, LIMIT_MOVIES_YEAR), 'w')

    f.write('year, movie title, url, spain gross, domestic gross, worldwide gross, budget, imdb\n')
    for row in summary:
        f.write('"' + '", "'.join(row) + '"\n')
    f.close()

def visit_movies(driver, year):

    xpath_matcher = "//a[contains(@href, 'release') and contains(@class, 'a-link-normal') and not(contains(@href, 'imdb'))]"
    anchors_len = len(driver.find_elements(By.XPATH, xpath_matcher))
    movie_summaries = []
    for i in range(anchors_len):
        anchor = driver.find_elements(By.XPATH, xpath_matcher)[i]
        if (anchor.text in ['Release Date', '']):
            continue
        anchor.click()
        time.sleep(1)
        movie_name = driver.find_element_by_class_name('a-size-extra-large').text
        money_table = driver.find_element_by_class_name('mojo-performance-summary-table')
        url = driver.current_url
        moneys = money_table.find_elements_by_class_name('a-text-bold')
        grosses = []
        budget = 'N/A'
        for money in moneys:
            grosses.append(money.text)
        try:
            budget = driver.find_element(By.XPATH, "//*[text()='Budget']/following-sibling::span").text
        except:
            print('No budget')

        imdb = driver.find_element(By.XPATH, "//*[text()='See more details at IMDbPro']").get_attribute('href')

        movie_summary = [year, movie_name, url, grosses[1], grosses[2], grosses[3], budget, imdb.replace('pro.imdb', 'imdb').split('?')[0]]

        movie_summaries.append(movie_summary)
        driver.back()
        if (i > LIMIT_MOVIES_YEAR):
            break
    return movie_summaries

if __name__ == '__main__':
    install_browser(FILE_DIR)
    driver = setup_chrome(FILE_DIR)
 
    driver.get(url)
    loop_table(driver)