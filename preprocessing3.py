import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import selenium.webdriver.support.expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.webdriver.common.keys import Keys
import pandas as pd
import csv

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

driver.get("https://www.capitaliq.spglobal.com/web/client?auth=inherit#industry/rateCalculator")
driver.implicitly_wait(4)
driver.find_element(By.NAME, "username").send_keys("jasonross@uchicago.edu")
driver.find_element(By.NAME, "password").send_keys("gyvfen-wujCe4-newxun")
driver.find_element(By.XPATH, '//*[@id="login-mfe-container"]/div/div/div/main/div/div/div/form/div[4]/div[1]/button').click()

driver.implicitly_wait(15)
driver.find_element(By.XPATH, '//*[@id="onetrust-accept-btn-handler"]').click()
time.sleep(3)
banner = driver.find_element(By.XPATH, '//*[@id="section_1_control_17"]/div[1]/div/span[2]')
try_button(banner)

table = pd.read_csv("./table2.csv")
pipeline_button = driver.find_element(By.XPATH, '//*[@id="section_1_control_21"]/div/div/div/label/div/button')
pipeline_names = list(table["Pipeline"])
table = table.set_index("Pipeline")

pipeline_dict = {pipeline: [] for pipeline in pipeline_names}
pipeline_button = driver.find_element(By.XPATH, '//*[@id="section_1_control_21"]/div/div/div/label/div/button')
pipeline_input = driver.find_element(By.XPATH, '//*[@id="section_1_control_21"]/div/div/div/label/div/div/div[2]/input')
receipt_button_0 = driver.find_element(By.XPATH, '//*[@id="section_1_control_34"]/div/div/div/label/div/button')
delivery_button_0 = driver.find_element(By.XPATH, '//*[@id="section_1_control_40"]/div/div/div/label/div/button')
receipt_button_1 = driver.find_element(By.XPATH, '//*[@id="section_1_control_31"]/div/div/div/label/div/button')
delivery_button_1 = driver.find_element(By.XPATH, '//*[@id="section_1_control_37"]/div/div/div/label/div/button')
receipt_clear = driver.find_element(By.XPATH, '//*[@id="section_1_control_31"]/div/div/div/label/div/div/div[1]/div[3]/a[2]')
delivery_clear = driver.find_element(By.XPATH, '//*[@id="section_1_control_37"]/div/div/div/label/div/div/div[1]/div[3]/a[2]')
apply_button = driver.find_element(By.XPATH, '//*[@id="Apply_section_1_control_18"]')

file = open(f'./table3.csv', 'w', newline = '')
file_writer = csv.writer(file, delimiter = ',', quoting = csv.QUOTE_MINIMAL)
file_writer.writerow(['Pipeline', 'Loc Desc', 'Zone', 'Point'])

for pipeline in pipeline_names:
    pipeline_button.click()
    pipeline_input.send_keys(pipeline)
    pipeline_input.send_keys(Keys.ENTER)
    time.sleep(1)

    info = list(table.loc[pipeline])
    if info[1] == 0:
        try_button(receipt_button_0)
        points_list = driver.find_element(By.XPATH, '//*[@id="section_1_control_34"]/div/div/div/label/div/div/ul')
        points_names_elements = points_list.find_elements(By.XPATH, './/span[@class = "text"]')
        points_names = [point.text for point in points_names_elements]
        file_writer.writerows([[pipeline, 'Receipt', 'Entire System', point] for point in points_names])
        try_button(receipt_button_0)
    else:
        for i, zone in enumerate(info[2].split(',')):
            try_button(receipt_button_1)
            receipt_clear.click()
            driver.find_element(By.XPATH, f'//*[@id="section_1_control_31"]/div/div/div/label/div/div/ul/li[{i + 1}]/a').click()
            receipt_button_1.click()
            try:
                receipt_button_0.click()
                points_list = driver.find_element(By.XPATH, '//*[@id="section_1_control_34"]/div/div/div/label/div/div/ul')
                points_names_elements = points_list.find_elements(By.XPATH, './/span[@class = "text"]')
                points_names = [point.text for point in points_names_elements]
                file_writer.writerows([[pipeline, 'Receipt', zone, point] for point in points_names])
                receipt_button_0.click()
            except (ElementClickInterceptedException, ElementNotInteractableException):
                continue

    if info[4] == 0:
        try_button(delivery_button_0)
        points_list = driver.find_element(By.XPATH, '//*[@id="section_1_control_40"]/div/div/div/label/div/div/ul')
        points_names_elements = points_list.find_elements(By.XPATH, './/span[@class = "text"]')
        points_names = [point.text for point in points_names_elements]
        file_writer.writerows([[pipeline, 'Delivery', 'Entire System', point] for point in points_names])
        delivery_button_0.click()
    else:
        for i, zone in enumerate(info[5].split(',')):
            try_button(delivery_button_1)
            delivery_clear.click()
            driver.find_element(By.XPATH, f'//*[@id="section_1_control_37"]/div/div/div/label/div/div/ul/li[{i + 1}]/a').click()
            delivery_button_1.click()
            try:
                delivery_button_0.click()
                points_list = driver.find_element(By.XPATH, '//*[@id="section_1_control_40"]/div/div/div/label/div/div/ul')
                points_names_elements = points_list.find_elements(By.XPATH, './/span[@class = "text"]')
                points_names = [point.text for point in points_names_elements]
                file_writer.writerows([[pipeline, 'Delivery', zone, point] for point in points_names])
                delivery_button_0.click()
            except (ElementClickInterceptedException, ElementNotInteractableException):
                continue

file.close()