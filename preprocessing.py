import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import selenium.webdriver.support.expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import pandas as pd

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
WebDriverWait(driver, timeout = 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="section_1_control_17"]/div[1]/div/span[2]'))).click()

pipeline_button = driver.find_element(By.XPATH, '//*[@id="section_1_control_21"]/div/div/div/label/div/button')
pipeline_button.click()
pipelines_list = driver.find_element(By.XPATH, '//*[@id="section_1_control_21"]/div/div/div/label/div/div/ul')
pipeline_names_elements = pipelines_list.find_elements(By.XPATH, '//span[@class = "text"]')
pipeline_names = [pipeline.text for pipeline in pipeline_names_elements]
pipeline_button.click()

pipeline_dict = {pipeline: [] for pipeline in pipeline_names}
pipeline_input = driver.find_element(By.XPATH, '//*[@id="section_1_control_21"]/div/div/div/label/div/div/div[2]/input')
rate_button = driver.find_element(By.XPATH, '//*[@id="section_1_control_27"]/div/div/div/label/div/button')
receipt_button_0 = driver.find_element(By.XPATH, '//*[@id="section_1_control_34"]/div/div/div/label/div/button')
delivery_button_0 = driver.find_element(By.XPATH, '//*[@id="section_1_control_40"]/div/div/div/label/div/button')
receipt_button_1 = driver.find_element(By.XPATH, '//*[@id="section_1_control_31"]/div/div/div/label/div/button')
delivery_button_1 = driver.find_element(By.XPATH, '//*[@id="section_1_control_37"]/div/div/div/label/div/button')

for pipeline in pipeline_names:
    pipeline_button.click()
    pipeline_input.send_keys(pipeline)
    pipeline_input.send_keys(Keys.ENTER)
    time.sleep(1)
    
    rate_button.click()
    button_list = driver.find_element(By.XPATH, f'//*[@id="section_1_control_27"]/div/div/div/label/div/div/ul')
    driver.implicitly_wait(1)
    num_elems = len(button_list.find_elements(By.TAG_NAME, 'li'))
    driver.implicitly_wait(1)
    pipeline_dict[pipeline].append(num_elems)
    rate_button.click()
    
    if receipt_button_1.get_attribute('aria-disabled') == "false":
        receipt_button_1.click()
        button_list = driver.find_element(By.XPATH, f'//*[@id="section_1_control_31"]/div/div/div/label/div/div/ul')
        driver.implicitly_wait(1)
        num_elems = len(button_list.find_elements(By.TAG_NAME, 'li'))
        driver.implicitly_wait(1)
        pipeline_dict[pipeline].append(num_elems)
        receipt_button_1.click()
        pipeline_dict[pipeline].append(1)
    else:
        receipt_button_0.click()
        button_list = driver.find_element(By.XPATH, f'//*[@id="section_1_control_34"]/div/div/div/label/div/div/ul')
        driver.implicitly_wait(1)
        num_elems = len(button_list.find_elements(By.TAG_NAME, 'li'))
        driver.implicitly_wait(1)
        pipeline_dict[pipeline].append(num_elems)
        receipt_button_0.click()
        pipeline_dict[pipeline].append(0)
        
    if delivery_button_1.get_attribute('aria-disabled') == "false":
        delivery_button_1.click()
        button_list = driver.find_element(By.XPATH, f'//*[@id="section_1_control_37"]/div/div/div/label/div/div/ul')
        driver.implicitly_wait(1)
        num_elems = len(button_list.find_elements(By.TAG_NAME, 'li'))
        driver.implicitly_wait(1)
        pipeline_dict[pipeline].append(num_elems)
        delivery_button_1.click()
        pipeline_dict[pipeline].append(1)
    else:
        delivery_button_0.click()
        button_list = driver.find_element(By.XPATH, f'//*[@id="section_1_control_40"]/div/div/div/label/div/div/ul')
        driver.implicitly_wait(1)
        num_elems = len(button_list.find_elements(By.TAG_NAME, 'li'))
        driver.implicitly_wait(1)
        pipeline_dict[pipeline].append(num_elems)
        delivery_button_0.click()
        pipeline_dict[pipeline].append(0)
    
dataframe = pd.DataFrame.from_dict(pipeline_dict, orient = 'index', columns = ['Number of Rate Schedules', 'Number of Recept Points', 'Need to Clear Receipt?', 'Number of Delivery Points', 'Need to Clear Delivery?'])
dataframe.to_csv('thing.csv')