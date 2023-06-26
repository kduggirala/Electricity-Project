import time
from selenium import webdriver
from selenium.webdriver.common.by import By
import selenium.webdriver.support.expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import ElementClickInterceptedException
import csv
from bs4 import BeautifulSoup 

def extract_data(quarter):
    global driver
    soup = BeautifulSoup(driver.page_source, 'lxml')
    table = soup.tbody
    table_rows = [tr("td") for tr in table("tr")]
    data = [[quarter] + [e1.div.span.contents[0], e2.div.span.contents[0]] + [e.div.contents[0] for e in rest] for e1, e2, *rest in table_rows]
    return [[s.replace(',', '') for s in data_row] for data_row in data]

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

driver.get("https://www.capitaliq.spglobal.com/web/client?auth=inherit#industry/ShipperContractSummary")
driver.implicitly_wait(4)
driver.find_element(By.NAME, "username").send_keys("jasonross@uchicago.edu")
driver.find_element(By.NAME, "password").send_keys("gyvfen-wujCe4-newxun")
driver.find_element(By.XPATH, '//*[@id="login-mfe-container"]/div/div/div/main/div/div/div/form/div[4]/div[1]/button').click()
driver.implicitly_wait(15)
cookie_button = driver.find_element(By.XPATH, '//*[@id="onetrust-accept-btn-handler"]')
try_button(cookie_button)
time.sleep(3)

banner = driver.find_element(By.XPATH, '//*[@id="section_1_control_15"]/div[1]/div/span[2]')
try_button(banner)
period_button = driver.find_element(By.XPATH, '//*[@id="section_1_control_25"]/div/div/label/div/button')
apply_all = driver.find_element(By.XPATH, '//*[@id="Apply_section_1_control_16"]')

file = open(f'./data/shipper_contract_summary.csv', 'w', newline = '')
file_writer = csv.writer(file, delimiter = ',', quoting = csv.QUOTE_MINIMAL)
soup = BeautifulSoup(driver.page_source, 'lxml')
table_header = soup("thead")[0]
fields = ['Quarter'] + [child.span.div.contents[0] for child in table_header.tr.children]
file_writer.writerow(fields)

quarters = ["Q2 2023", "Q1 2023"] + [f"Q{i} 20{j}" for j in range(22, 16, -1) for i in range(4, 0, -1)]
for i, quarter in enumerate(quarters):
    try_button(period_button)
    driver.find_element(By.XPATH, f'//*[@id="section_1_control_25"]/div/div/label/div/div/ul/li[{i + 1}]').click()
    try_button(apply_all)
    time.sleep(1)
    file_writer.writerows(extract_data(quarter))
    status = driver.find_element(By.XPATH, f'//*[@class="ui-iggrid-nextpage ui-iggrid-paging-item ui-state-default"]/span[1]').get_attribute("class")
    while status == "ui-iggrid-nextpagelabel":
        try_button(driver.find_element(By.XPATH, '//*[@class="ui-iggrid-nextpage ui-iggrid-paging-item ui-state-default"]'))
        time.sleep(0.5)
        file_writer.writerows(extract_data(quarter))
        status = driver.find_element(By.XPATH, f'//*[@class="ui-iggrid-nextpage ui-iggrid-paging-item ui-state-default"]/span[1]').get_attribute("class")
    try_button(banner)
file.close()
    
