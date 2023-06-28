import time
from selenium import webdriver
from selenium.webdriver.common.by import By
import selenium.webdriver.support.expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import ElementClickInterceptedException
import csv
from bs4 import BeautifulSoup 

def extract_data():
    global driver
    soup = BeautifulSoup(driver.page_source, 'lxml')
    if not soup("tbody"):
        #if there's no data
        return
    left_table, right_table = soup("tbody")
    f = lambda e : e.div
    identity = lambda e : e
    d = {i : identity if i in [14,15,16,17] else f for i in range(1,20)}
    d[0] = lambda e : e.div.span
    left_data = [e.td.div.span for e in left_table("tr")]
    data = [[left_data[i]] + [d[j](e) for j, e in enumerate(tr("td"))] for i, tr in enumerate(right_table("tr"))]
    return [[e.contents[0].replace(',', '') for e in row] for row in data]

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

driver.get("https://www.capitaliq.spglobal.com/web/client?auth=inherit#industry/ShipperContractDetails")
driver.implicitly_wait(4)
driver.find_element(By.NAME, "username").send_keys("jasonross@uchicago.edu")
driver.find_element(By.NAME, "password").send_keys("gyvfen-wujCe4-newxun")
driver.find_element(By.XPATH, '//*[@id="login-mfe-container"]/div/div/div/main/div/div/div/form/div[4]/div[1]/button').click()
driver.implicitly_wait(10)
cookie_button = driver.find_element(By.XPATH, '//*[@id="onetrust-accept-btn-handler"]')
try_button(cookie_button)
time.sleep(2)

soup = BeautifulSoup(driver.page_source, 'lxml')
table_header = soup("thead")[1]
fields = ['Shipper Name'] + [child.span.div.contents[0] for child in table_header.tr.children]

for qtr in range(1,27):
    banner = driver.find_element(By.XPATH, '//*[@id="section_1_control_19"]/div[1]/div')
    try_button(banner)
    quarter_button = driver.find_element(By.XPATH, '//*[@id="section_1_control_29"]/div/div/label/div/button')
    shipper_button = driver.find_element(By.XPATH, '//*[@id="section_1_control_38"]/div/div/label/div/button')
    clear_all = driver.find_element(By.XPATH, '//*[@id="section_1_control_38"]/div/div/label/div/div/div[1]/div[3]/a')
    apply_all = driver.find_element(By.XPATH, '//*[@id="Apply_section_1_control_20"]')

    file = open(f'./data/shipper_data_raw/shipper_details_{qtr}.csv', 'w', newline = '')
    file_writer = csv.writer(file, delimiter = ',', quoting = csv.QUOTE_MINIMAL)
    file_writer.writerow(fields)

    quarter_button.click()
    driver.find_element(By.XPATH, f'//*[@id="section_1_control_29"]/div/div/label/div/div/ul/li[{qtr}]/a').click()
    time.sleep(0.1)
    shipper_button.click()
    soup = BeautifulSoup(driver.page_source, 'lxml')
    num_shippers = len(list(soup.find_all("ul", {"class": "dropdown-menu inner"})[1].children))
    shipper_button.click()
    for i in range(1, num_shippers + 1, 20):
        try_button(shipper_button)
        try_button(clear_all)
        for j in range(i, min(i + 20, num_shippers + 1)):
            driver.find_element(By.XPATH, f'//*[@id="section_1_control_38"]/div/div/label/div/div/ul/li[{j}]/a').click()
        try_button(shipper_button)
        try_button(apply_all)
        try_button(banner)
        file_writer.writerows(extract_data())

        status = driver.find_element(By.XPATH, f'//*[@class="ui-iggrid-nextpage ui-iggrid-paging-item ui-state-default"]/span[1]').get_attribute("class")
        while status == "ui-iggrid-nextpagelabel":
            try_button(driver.find_element(By.XPATH, '//*[@class="ui-iggrid-nextpage ui-iggrid-paging-item ui-state-default"]'))
            time.sleep(0.2)
            file_writer.writerows(extract_data())
            status = driver.find_element(By.XPATH, f'//*[@class="ui-iggrid-nextpage ui-iggrid-paging-item ui-state-default"]/span[1]').get_attribute("class")
        try_button(apply_all)
        try_button(banner)

        file.flush()
    file.close()
    driver.get(driver.current_url)
    driver.refresh()