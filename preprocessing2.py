import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import selenium.webdriver.support.expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.common.keys import Keys
import pandas as pd

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
try_button(banner)

table = pd.read_csv("/Users/kdugg/OneDrive/Documents/Python Scripts/ElectricityProject/table.csv")
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

for pipeline in pipeline_names:
    info = list(table.loc[pipeline])
    if not info[2]:
        pipeline_dict[pipeline] = [info[0], 0, '', '', 0, '', '']
        continue
    pipeline_button.click()
    pipeline_input.send_keys(pipeline)
    pipeline_input.send_keys(Keys.ENTER)
    time.sleep(1)
    receipt_names = []
    receipt_point_names = []
    for i in range(1, info[1] + 1):
        try_button(receipt_button_1)
        receipt_clear.click()
        list_item = driver.find_element(By.XPATH, f'//*[@id="section_1_control_31"]/div/div/div/label/div/div/ul/li[{i}]/a')
        name = list_item.find_element(By.XPATH, f'//*[@id="section_1_control_31"]/div/div/div/label/div/div/ul/li[{i}]/a/span[1]').text
        list_item.click()
        receipt_button_1.click()
        try_button(apply_button)
        try_button(banner)
        if receipt_button_0.get_attribute('aria-disabled') != "true":
            receipt_names.append(name)
            receipt_point_name = receipt_button_0.get_attribute('title').replace(',', ' ')
            receipt_point_names.append(receipt_point_name)
    
    if not info[4]:
        pipeline_dict[pipeline] = [info[0], info[1], ','.join(receipt_names), ','.join(receipt_point_names), 0, '', delivery_button_0.get_attribute('title')]
        continue
    
    delivery_names = []
    delivery_point_names = []
    for i in range(1, info[3] + 1):
        try_button(delivery_button_1)
        delivery_clear.click()
        list_item = driver.find_element(By.XPATH, f'//*[@id="section_1_control_37"]/div/div/div/label/div/div/ul/li[{i}]/a')
        name = list_item.find_element(By.XPATH, f'//*[@id="section_1_control_37"]/div/div/div/label/div/div/ul/li[{i}]/a/span[1]').text
        list_item.click()
        delivery_button_1.click()
        try_button(apply_button)
        try_button(banner)
        if delivery_button_0.get_attribute('aria-disabled') != "true":
            delivery_names.append(name)
            delivery_point_name = delivery_button_0.get_attribute('title').replace(',', ' ')
            delivery_point_names.append(delivery_point_name)

    pipeline_dict[pipeline] = [info[0], info[1], ','.join(receipt_names), ','.join(receipt_point_names), info[3], ','.join(delivery_names), ','.join(delivery_point_names)]
    
dataframe = pd.DataFrame.from_dict(pipeline_dict, orient = 'index', columns = ['Number of Rate Schedules', 'Number of Receipt Zones', 'Valid Receipt Zones Names', 'Valid Receipt Points Names', 'Number of Delivery Zones', 'Valid Delivery Zones Names', 'Valid Delivery Points Names'])
dataframe.to_csv('table2.csv')