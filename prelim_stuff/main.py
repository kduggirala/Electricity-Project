import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import selenium.webdriver.support.expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementClickInterceptedException
import pandas as pd
import csv
from bs4 import BeautifulSoup 

def extract_data(driver, record, file_writer):
    soup = BeautifulSoup(driver.page_source, 'lxml')
    table = soup.tbody
    if not table:
        return
    table_rows = [list(child.children) for child in table.children]
    try:
        #if the table has data, it'll be structure as rows of 5 elements
        data_rows = [record + [e1.contents[0], e2.div.contents[0], e3.contents[0], e4.contents[0], e5.contents[0]] for [e1, e2, e3, e4, e5] in table_rows]
        file_writer.writerows(data_rows)
    except ValueError:
        #otherwise, the table has no data, so we return
        return

c = webdriver.ChromeOptions()
c.add_argument("--incognito")
driver = webdriver.Chrome(options = c)
driver.maximize_window()

driver.get("https://www.capitaliq.spglobal.com/web/client?auth=inherit#news/home")
driver.implicitly_wait(4)
driver.find_element(By.NAME, "username").send_keys("jasonross@uchicago.edu")
driver.find_element(By.NAME, "password").send_keys("gyvfen-wujCe4-newxun")
driver.find_element(By.XPATH, '//*[@id="login-mfe-container"]/div/div/div/main/div/div/div/form/div[4]/div[1]/button').click()

driver.implicitly_wait(15)
driver.find_element(By.XPATH, '//*[@id="onetrust-accept-btn-handler"]').click()
time.sleep(3)
driver.find_element(By.XPATH, '//*[@id="snl-navigation-top-menu"]/div/ul/li[6]/a').click()
driver.find_element(By.XPATH, '//*[@id="snl-navigation-top-menu"]/div/ul/li[6]/div/div/div[2]/ul[3]/li/a').click()
banner = driver.find_element(By.XPATH, '//*[@id="section_1_control_17"]/div[1]/div/span[2]')
WebDriverWait(driver, timeout = 10).until(EC.element_to_be_clickable(banner)).click()

table = pd.read_csv("table.csv")
pipelines = list(table["Pipeline"])
table = table.set_index("Pipeline")
file = open('rate_data_07-01-2018.csv', 'w', newline = '')
file_writer = csv.writer(file, delimiter = ',', quoting = csv.QUOTE_MINIMAL)
file_writer.writerow(['Pipeline', 'Date', 'Rate Schedule', 'Receipt Point', 'Receipt Zone', 'Delivery Point', 'Delivery Zone', 'Tariff Rate Type', 'Tariff Rate', 'Magnitude', 'Tariff Rate Structure', 'Rate Zone'])

date = '07/01/2018'
date_input = driver.find_element(By.XPATH, '//*[@id="section_1_control_25_startdate"]')
date_input.clear()
date_input.send_keys(date)
date_input.send_keys(Keys.ENTER)

#relevant buttons on the site:
pipeline_button = driver.find_element(By.XPATH, '//*[@id="section_1_control_21"]/div/div/div/label/div/button')
pipeline_input = driver.find_element(By.XPATH, '//*[@id="section_1_control_21"]/div/div/div/label/div/div/div[2]/input')
rate_button = driver.find_element(By.XPATH, '//*[@id="section_1_control_27"]/div/div/div/label/div/button')
receipt_button_0 = driver.find_element(By.XPATH, '//*[@id="section_1_control_34"]/div/div/div/label/div/button')
delivery_button_0 = driver.find_element(By.XPATH, '//*[@id="section_1_control_40"]/div/div/div/label/div/button')
receipt_button_1 = driver.find_element(By.XPATH, '//*[@id="section_1_control_31"]/div/div/div/label/div/button')
delivery_button_1 = driver.find_element(By.XPATH, '//*[@id="section_1_control_37"]/div/div/div/label/div/button')
receipt_clear = driver.find_element(By.XPATH, '//*[@id="section_1_control_31"]/div/div/div/label/div/div/div[1]/div[3]/a[2]')
delivery_clear = driver.find_element(By.XPATH, '//*[@id="section_1_control_37"]/div/div/div/label/div/div/div[1]/div[3]/a[2]')
apply_button = driver.find_element(By.XPATH, '//*[@id="Apply_section_1_control_18"]')

for pipeline in pipelines:
    record = [pipeline, date] + [""]*5
    pipeline_button.click()
    pipeline_input.send_keys(pipeline)
    pipeline_input.send_keys(Keys.ENTER)
    time.sleep(1)
    info = list(table.loc[pipeline])
    for rate in range(1, info[0] + 1):
        rate_button.click()
        list_item = driver.find_element(By.XPATH, f'//*[@id="section_1_control_27"]/div/div/div/label/div/div/ul/li[{rate}]/a')
        record[2] = list_item.find_element(By.XPATH, f'//*[@id="section_1_control_27"]/div/div/div/label/div/div/ul/li[{rate}]/a/span[1]').text
        list_item.click()
        if info[2]:
            for receipt in range(1, info[1] + 1):
                receipt_button_1.click()
                receipt_clear.click()
                list_item = driver.find_element(By.XPATH, f'//*[@id="section_1_control_31"]/div/div/div/label/div/div/ul/li[{receipt}]/a')
                record[4] = list_item.find_element(By.XPATH, f'//*[@id="section_1_control_31"]/div/div/div/label/div/div/ul/li[{receipt}]/a/span[1]').text
                list_item.click()
                receipt_button_1.click()
                record[3] = 'NaN' if receipt_button_0.get_attribute('aria-disabled') == "true" else receipt_button_0.get_attribute('title')
                driver.implicitly_wait(2)
                if info[3]:
                    for delivery in range(1, info[3] + 1):
                        delivery_button_1.click()
                        delivery_clear.click()
                        list_item = driver.find_element(By.XPATH, f'//*[@id="section_1_control_37"]/div/div/div/label/div/div/ul/li[{delivery}]/a')
                        record[6] = list_item.find_element(By.XPATH, f'//*[@id="section_1_control_37"]/div/div/div/label/div/div/ul/li[{delivery}]/a/span[1]').text
                        list_item.click()
                        delivery_button_1.click()
                        record[5] = 'NaN' if delivery_button_0.get_attribute('aria-disabled') == "true" else delivery_button_0.get_attribute('title')
                            
                        try:
                            WebDriverWait(driver, timeout = 15).until(EC.element_to_be_clickable(apply_button)).click()
                        except ElementClickInterceptedException:
                            time.sleep(2)
                            apply_button.click()
                        extract_data(driver, record, file_writer)
                        file.flush()
                        try:
                            WebDriverWait(driver, timeout = 15).until(EC.element_to_be_clickable(banner)).click()
                        except ElementClickInterceptedException:
                            time.sleep(3)
                            banner.click()
                else:
                    record[5] = delivery_button_0.get_attribute('title')
                    record[6] = 'NaN'
                    try:
                        WebDriverWait(driver, timeout = 15).until(EC.element_to_be_clickable(apply_button)).click()
                    except ElementClickInterceptedException:
                        time.sleep(2)
                        apply_button.click()
                    extract_data(driver, record, file_writer)
                    file.flush()
                    try:
                        WebDriverWait(driver, timeout = 15).until(EC.element_to_be_clickable(banner)).click()
                    except ElementClickInterceptedException:
                        try: 
                            time.sleep(3)
                            banner.click()
                        except ElementClickInterceptedException:
                            time.sleep(10)
                            banner.click()
            
        else:
            record[3] = receipt_button_0.get_attribute('title')
            record[4] = 'NaN'
            record[5] = delivery_button_0.get_attribute('title')
            record[6] = 'NaN'
            apply_button.click()
            extract_data(driver, record, file_writer)
            file.flush()
            try:
                WebDriverWait(driver, timeout = 15).until(EC.element_to_be_clickable(banner)).click()
            except ElementClickInterceptedException:
                time.sleep(5)
                banner.click()
                