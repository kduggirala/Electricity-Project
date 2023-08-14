import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
import selenium.webdriver.support.expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import ElementClickInterceptedException
import csv
from bs4 import BeautifulSoup 

def extract_data(reg):
    global driver
    soup = BeautifulSoup(driver.page_source, 'lxml')
    if not soup("thead"):
        return []
    terms, data= soup("tbody")
    locs = soup("thead")[1].tr("th")
    locs = [e.span.contents[0] for e in locs]
    terms = [e.td.contents[0] for e in terms("tr")]
    data = [[e.div.contents[0] for e in row("td")] for row in data("tr")]
    n = len(locs)
    data_rows = []
    for j in range(n):
        data_j = [row[j] for row in data]
        for k in range(len(data_j)):
            if data_j[k] != "NA":
                data_rows.append([reg, terms[k], locs[j], data_j[k]])

    return data_rows


def try_button(button):
    global driver
    try:
        WebDriverWait(driver, timeout = 10).until(EC.element_to_be_clickable(button)).click()
    except ElementClickInterceptedException:
        time.sleep(1)
        try_button(button)

c = webdriver.ChromeOptions()
c.add_argument("--incognito")
driver = webdriver.Chrome(options = c)
driver.maximize_window()

driver.get("https://www.capitaliq.spglobal.com/web/client?auth=inherit#markets/snlDayAheadGas?key=982fafdb-b14f-4c18-b151-75be96d6c2c5")
driver.implicitly_wait(4)
driver.find_element(By.NAME, "username").send_keys("jasonross@uchicago.edu")
driver.find_element(By.NAME, "password").send_keys("gyvfen-wujCe4-newxun")
driver.find_element(By.XPATH, '//*[@id="login-mfe-container"]/div/div/div/main/div/div/div/form/div[4]/div[1]/button').click()
driver.implicitly_wait(15)
driver.find_element(By.XPATH, '//*[@id="onetrust-accept-btn-handler"]').click()
time.sleep(3)

driver.find_element(By.XPATH, '//*[@id="section_1_control_35"]').click()
banner = driver.find_element(By.XPATH, '//*[@id="section_1_control_19"]/div[1]/div/span[2]')
try_button(banner)
region = driver.find_element(By.XPATH, '//*[@id="section_1_control_22"]/div/div/div/label/div/button')
asof = driver.find_element(By.XPATH, '//*[@id="section_1_control_25_startdate"]')
apply_all = driver.find_element(By.XPATH, '//*[@id="Apply_section_1_control_20"]')


with open(f'./data/dayahead0.csv', 'w', newline = '') as file:   
    file_writer = csv.writer(file, delimiter = ',', quoting = csv.QUOTE_MINIMAL)
    file_writer.writerow(['Region', 'Date', 'Location', 'Price'])
    for j, reg in enumerate(['Gulf Coast-LA', 'Gulf Coast-Non TX/LA', 'Gulf Coast-TX', 'Mid-Continent North', 'Mid-Continent South', 'Northeast-Non NY/NE', 'Northeast-NY/NE', 'West-Rockies', 'West-Southwest', 'West-West Coast']):
        region.click()
        driver.find_element(By.XPATH, f'//*[@id="section_1_control_22"]/div/div/div/label/div/div/ul/li[{j + 1}]/a').click()
        date = '8/11/2023'
        min_date = pd.to_datetime('8/11/2013')
        while pd.to_datetime(date) > min_date:
            asof.clear()
            asof.send_keys(date)
            asof.send_keys(Keys.ENTER)
            apply_all.click()

            try_button(banner)
            data = extract_data(reg)
            file_writer.writerows(data)
            date = data[-1][1]
        date = '8/11/2013'
        asof.clear()
        asof.send_keys(date)
        asof.send_keys(Keys.ENTER)
        apply_all.click()

        try_button(banner)
        data = extract_data(reg)
        file_writer.writerows(data)