import time
from selenium import webdriver
from selenium.webdriver.common.by import By
import selenium.webdriver.support.expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import ElementClickInterceptedException
import csv
from bs4 import BeautifulSoup 

def extract_data(quarter, pipeline):
    global driver
    soup = BeautifulSoup(driver.page_source, 'lxml')
    table = soup("tbody")[1]
    rows = []
    for tr in table("tr"):
        e1, *tds = tr("td")
        rows.append([quarter, pipeline] + [e1.div.span.contents[0].replace(',', '')] + [str(td.div.contents[0]).replace(',', '') for td in tds])
    return rows

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

driver.get("https://www.capitaliq.spglobal.com/web/client?auth=inherit#industry/PipelineContractDetails")
driver.implicitly_wait(4)
driver.find_element(By.NAME, "username").send_keys("jasonross@uchicago.edu")
driver.find_element(By.NAME, "password").send_keys("gyvfen-wujCe4-newxun")
driver.find_element(By.XPATH, '//*[@id="login-mfe-container"]/div/div/div/main/div/div/div/form/div[4]/div[1]/button').click()
driver.implicitly_wait(10)
driver.find_element(By.XPATH, '//*[@id="onetrust-accept-btn-handler"]').click()
time.sleep(3)

soup = BeautifulSoup(driver.page_source, 'lxml')
table_header = soup("thead")[1]
fields = ['Quarter', 'Pipeline'] + [child.span.div.contents[0] for child in table_header.tr.children]

for qtr in range(1,27):
    banner = driver.find_element(By.XPATH, '//*[@id="section_1_control_19"]/div[1]/div')
    try_button(banner)
    quarter_button = driver.find_element(By.XPATH, '//*[@id="section_1_control_29"]/div/div/label/div/button')
    pipeline_button = driver.find_element(By.XPATH, '//*[@id="section_1_control_38"]/div/div/label/div/button')
    clear_all = driver.find_element(By.XPATH, '//*[@id="section_1_control_38"]/div/div/label/div/div/div[1]/div[3]/a')
    apply_all = driver.find_element(By.XPATH, '//*[@id="Apply_section_1_control_20"]')

    file = open(f'./data/contract_data/contract_details_{qtr}.csv', 'w', newline = '')
    file_writer = csv.writer(file, delimiter = ',', quoting = csv.QUOTE_MINIMAL)
    file_writer.writerow(fields)

    quarter_button.click()
    quarter = driver.find_element(By.XPATH, f'//*[@id="section_1_control_29"]/div/div/label/div/div/ul/li[{qtr}]/a/span[1]').text
    driver.find_element(By.XPATH, f'//*[@id="section_1_control_29"]/div/div/label/div/div/ul/li[{qtr}]/a').click()
    time.sleep(0.1)
    pipeline_button.click()
    soup = BeautifulSoup(driver.page_source, 'lxml')
    num_pipelines = len(list(soup.find_all("ul", {"class": "dropdown-menu inner"})[1].children))
    pipeline_button.click()
    for i in range(1, num_pipelines + 1):
        try_button(pipeline_button)
        try_button(clear_all)
        driver.find_element(By.XPATH, f'//*[@id="section_1_control_38"]/div/div/label/div/div/ul/li[{i}]/a').click()
        pipeline = driver.find_element(By.XPATH, f'//*[@id="section_1_control_38"]/div/div/label/div/div/ul/li[{i}]/a/span[1]').text
        try_button(pipeline_button)
        try_button(apply_all)
        try_button(banner)
        file_writer.writerows(extract_data(quarter, pipeline))

        status = driver.find_element(By.XPATH, f'//*[@class="ui-iggrid-nextpage ui-iggrid-paging-item ui-state-default"]/span[1]').get_attribute("class")
        while status == "ui-iggrid-nextpagelabel":
            try_button(driver.find_element(By.XPATH, '//*[@class="ui-iggrid-nextpage ui-iggrid-paging-item ui-state-default"]'))
            time.sleep(0.5)
            file_writer.writerows(extract_data(quarter, pipeline))
            status = driver.find_element(By.XPATH, f'//*[@class="ui-iggrid-nextpage ui-iggrid-paging-item ui-state-default"]/span[1]').get_attribute("class")
        try_button(apply_all)
        try_button(banner)

        file.flush()
    file.close()
    driver.get(driver.current_url)
    time.sleep(1)
    driver.refresh()