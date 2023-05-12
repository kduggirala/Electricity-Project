import time
from selenium import webdriver
from selenium.webdriver.common.by import By
import selenium.webdriver.support.expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import ElementClickInterceptedException
import csv
from bs4 import BeautifulSoup 

def extract_data(company):
    global driver
    soup = BeautifulSoup(driver.page_source, 'lxml')
    left_table, right_table = soup("tbody")
    left_data = [tr.td.contents[0].split(' ') + [company] for tr in left_table("tr")]
    right_data = [[str(td.div.contents[0]).replace(',', '') for td in tr("td")] for tr in right_table("tr")]
    return [left_data[i] + right_data[i] for i in range(len(left_data))]

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

driver.get("https://www.capitaliq.spglobal.com/web/client?auth=inherit#industry/GasRetail")
driver.implicitly_wait(4)
driver.find_element(By.NAME, "username").send_keys("jasonross@uchicago.edu")
driver.find_element(By.NAME, "password").send_keys("gyvfen-wujCe4-newxun")
driver.find_element(By.XPATH, '//*[@id="login-mfe-container"]/div/div/div/main/div/div/div/form/div[4]/div[1]/button').click()
driver.implicitly_wait(15)
driver.find_element(By.XPATH, '//*[@id="onetrust-accept-btn-handler"]').click()
time.sleep(3)

driver.find_element(By.XPATH, '//*[@id="section_1_control_43"]/a').click()
banner = driver.find_element(By.XPATH, '//*[@id="section_1_control_18"]/div[1]/div/span[2]')
try_button(banner)
driver.find_element(By.XPATH, '//*[@id="section_1_control_20"]/div/div/label/div/button').click()
driver.find_element(By.XPATH, '//*[@id="section_1_control_20"]/div/div/label/div/div/ul/li[3]/a').click()

company_button = driver.find_element(By.XPATH, '//*[@id="section_1_control_31"]/div/div/label/div/button')
clear_all = driver.find_element(By.XPATH, '//*[@id="section_1_control_31"]/div/div/label/div/div/div[1]/div[3]/a[2]')
apply_all = driver.find_element(By.XPATH, '//*[@id="Apply_section_1_control_19"]')

file = open(f'./data/retail_gas_sales.csv', 'w', newline = '')
file_writer = csv.writer(file, delimiter = ',', quoting = csv.QUOTE_MINIMAL)
soup = BeautifulSoup(driver.page_source, 'lxml')

table_header = soup("thead")[1]
fields = [child.span.div.contents[0] for child in table_header.tr.children]
file_writer.writerow(['Company', 'Year', 'State'] + fields)
num_companies = 1578

for i in range(1, num_companies + 1):
    try_button(company_button)
    try_button(clear_all)
    driver.find_element(By.XPATH, f'//*[@id="section_1_control_31"]/div/div/label/div/div/ul/li[{i}]').click()
    company = driver.find_element(By.XPATH, f'//*[@id="section_1_control_31"]/div/div/label/div/div/ul/li[{i}]/a/span[1]').text
    try_button(company_button)
    try_button(apply_all)
    try_button(banner)
    file_writer.writerows(extract_data(company))

file.close()
    