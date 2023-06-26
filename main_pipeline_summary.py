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
    if not table:
        return None
    table_rows = [list(child.children) for child in table.children]
    try:
        #if the table has data, it'll be structure as rows of 7 elements
        data_rows = [[e1.div.span.contents[0], e2.div.contents[0], e3.div.contents[0], e4.div.contents[0], e5.div.contents[0], e6.div.contents[0], e7.div.contents[0]] for [e1, e2, e3, e4, e5, e6, e7] in table_rows]
        return [[quarter] + [str(e).replace(',', '') for e in row] for row in data_rows]
    except ValueError:
        #otherwise, the table has no data, so we return
        return None

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

driver.get("https://www.capitaliq.spglobal.com/web/client?auth=inherit#industry/PipelineContractSummary")
driver.implicitly_wait(4)
driver.find_element(By.NAME, "username").send_keys("jasonross@uchicago.edu")
driver.find_element(By.NAME, "password").send_keys("gyvfen-wujCe4-newxun")
driver.find_element(By.XPATH, '//*[@id="login-mfe-container"]/div/div/div/main/div/div/div/form/div[4]/div[1]/button').click()
driver.implicitly_wait(15)
driver.find_element(By.XPATH, '//*[@id="onetrust-accept-btn-handler"]').click()
time.sleep(3)

banner = driver.find_element(By.XPATH, '//*[@id="section_1_control_15"]/div[1]/div/span[2]')
try_button(banner)
period_button = driver.find_element(By.XPATH, '//*[@id="section_1_control_25"]/div/div/label/div/button')
pipelines_button = driver.find_element(By.XPATH, '//*[@id="section_1_control_34"]/div/div/div[1]/label/div/button')
select_all = driver.find_element(By.XPATH, '//*[@id="section_1_control_34"]/div/div/div[1]/label/div/div/div[1]/div[3]/a[1]')
apply_all = driver.find_element(By.XPATH, '//*[@id="Apply_section_1_control_16"]')

try_button(pipelines_button)
try_button(select_all)
try_button(pipelines_button)
file = open(f'./data/contract_summary.csv', 'w', newline = '')
file_writer = csv.writer(file, delimiter = ',', quoting = csv.QUOTE_MINIMAL)
file_writer.writerow(['Quarter', 'Pipeline', 'Total Daily Transportation (DTH)', 'Monthly Est. Transportation Reservation Revenue ($)', 'Total Storage (DTH)', 'Monthly Estimated Storage Reservation Revenue ($)', 'Average Contract Length (Months)', 'Active Contracts'])
quarters = ["Q2 2023", "Q1 2023"] + [f"Q{i} 20{j}" for j in range(22, 16) for i in range(4, 0, -1)]

for i, quarter in enumerate(quarters):
    try_button(period_button)
    driver.find_element(By.XPATH, f'//*[@id="section_1_control_25"]/div/div/label/div/div/ul/li[{i + 1}]').click()
    try_button(apply_all)
    time.sleep(1)
    file_writer.writerows(extract_data(quarter))
    try_button(banner)
file.close()
    
