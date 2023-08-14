import time
from selenium import webdriver
from selenium.webdriver.common.by import By
import selenium.webdriver.support.expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import ElementClickInterceptedException
import csv
from bs4 import BeautifulSoup 

def extract_data(src, reg, date):
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
                data_rows.append([date, src, reg, terms[k], locs[j], data_j[k]])

    return data_rows


def try_button(button):
    global driver
    try:
        WebDriverWait(driver, timeout = 10).until(EC.element_to_be_clickable(button)).click()
    except ElementClickInterceptedException:
        time.sleep(1)
        try_button(button)

def generate_dates(month, day,year, count, until_year):
    months = {i : 31 if i in [1,3,5,7,8,10,12] else 30 for i in range(1, 13)}
    months[2] = 28
    dates = []
    while year > until_year:
        dates.append(f"{month}/{day}/20{year}")
        if count == 0:
            count = 4
            day -= 3
        else:
            count -= 1
            day -= 1
        if day <= 0:
            month -= 1
            if month == 0:
                month = 12
                year -= 1
            if month == 2 and year % 4 == 0:
                day += 29
            else:
                day += months[month]
    return dates



c = webdriver.ChromeOptions()
c.add_argument("--incognito")
driver = webdriver.Chrome(options = c)
driver.maximize_window()

driver.get("https://www.capitaliq.spglobal.com/web/client?auth=inherit#markets/gasFutures?key=982fafdb-b14f-4c18-b151-75be96d6c2c5")
driver.implicitly_wait(4)
driver.find_element(By.NAME, "username").send_keys("jasonross@uchicago.edu")
driver.find_element(By.NAME, "password").send_keys("gyvfen-wujCe4-newxun")
driver.find_element(By.XPATH, '//*[@id="login-mfe-container"]/div/div/div/main/div/div/div/form/div[4]/div[1]/button').click()
driver.implicitly_wait(15)
driver.find_element(By.XPATH, '//*[@id="onetrust-accept-btn-handler"]').click()
time.sleep(3)

driver.find_element(By.XPATH, '//*[@id="section_1_control_41"]').click()
banner = driver.find_element(By.XPATH, '//*[@id="section_1_control_19"]/div[1]/div/span[2]')
try_button(banner)
source = driver.find_element(By.XPATH, '//*[@id="section_1_control_21"]/div/div/div[2]/label/div/button')
region = driver.find_element(By.XPATH, '//*[@id="section_1_control_29"]/div/div/div[2]/label/div/button')
asof = driver.find_element(By.XPATH, '//*[@id="section_1_control_33_startdate"]')
apply_all = driver.find_element(By.XPATH, '//*[@id="Apply_section_1_control_20"]')


with open(f'./data/futures.csv', 'w', newline = '') as file:   
    file_writer = csv.writer(file, delimiter = ',', quoting = csv.QUOTE_MINIMAL)
    file_writer.writerow(['Quote Day', 'Source', 'Region', 'Term', 'Location', 'Price'])
    for i, src in enumerate(['Amerex', 'CME Group/NYMEX', 'MI Forward', 'Tradition']):
        source.click()
        driver.find_element(By.XPATH, f'//*[@id="section_1_control_21"]/div/div/div[2]/label/div/div/ul/li[{i + 1}]/a').click()
        for j, reg in enumerate(['Gulf Coast-LA', 'Gulf Coast-Non TX/LA', 'Gulf Coast-TX', 'Mid-Continent North', 'Mid-Continent South', 'Northeast-Non NY/NE', 'Northeast-NY/NE', 'West-Rockies', 'West-Southwest', 'West-West Coast']):
            region.click()
            driver.find_element(By.XPATH, f'//*[@id="section_1_control_29"]/div/div/div[2]/label/div/div/ul/li[{j + 1}]/a').click()
            for date in generate_dates(8, 7, 23, 0, 9):
                asof.clear()
                asof.send_keys(date)
                asof.send_keys(Keys.ENTER)
                try_button(apply_all)
                try_button(banner)

                data = extract_data(src, reg, date)
                if data == []:
                    break
                file_writer.writerows(data)

                status = driver.find_element(By.XPATH, '//*[@class="ui-iggrid-nextpage ui-iggrid-paging-item ui-state-default"]/span[1]').get_attribute("class")
                while status == "ui-iggrid-nextpagelabel":
                    try_button(driver.find_element(By.XPATH, '//*[@class="ui-iggrid-nextpage ui-iggrid-paging-item ui-state-default"]'))
                    time.sleep(0.2)
                    file_writer.writerows(extract_data(src, reg, date))
                    status = driver.find_element(By.XPATH, f'//*[@class="ui-iggrid-nextpage ui-iggrid-paging-item ui-state-default"]/span[1]').get_attribute("class")
                driver.execute_script("window.scrollTo(0, document.body.scrollTop);")
