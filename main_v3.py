import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import selenium.webdriver.support.expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import TimeoutException
import pandas as pd
import csv
from bs4 import BeautifulSoup 

global receipt_button_0
global delivery_button_0 
global receipt_button_1
global delivery_button_1
global receipt_clear
global delivery_clear
global apply_button
global banner
global driver

def extract_data():
    global driver
    soup = BeautifulSoup(driver.page_source, 'lxml')
    table = soup.tbody
    if not table:
        return None
    table_rows = [list(child.children) for child in table.children]
    try:
        #if the table has data, it'll be structure as rows of 5 elements
        data_rows = [[e1.contents[0], e2.div.contents[0], e3.contents[0], e4.contents[0], e5.contents[0]] for [e1, e2, e3, e4, e5] in table_rows]
        return data_rows
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
    except TimeoutException:
        try_button(apply_button)
        try_button(banner)
        try_button(button)

def write_through_deliveries(record, info, file_writer, rows):
    delivery_zones = info[5].split(',')
    delivery_points = info[6].split(',')
    for i, _ in enumerate(delivery_zones):
        record[6] = delivery_zones[i]
        record[5] = delivery_points[i]
        file_writer.writerows([record + row for row in rows])

def write_through_receipts(record, info, file_writer, rows):
    receipt_zones = info[2].split(',')
    receipt_points = info[3].split(',')
    if not info[4]:
        for i, _ in enumerate(receipt_zones):
            record[4] = receipt_zones[i]
            record[3] = receipt_points[i]
            record[6] = "NaN"
            record[5] = info[6]
            file_writer.writerows([record + row for row in rows])
    else:
        for i, _ in enumerate(receipt_zones):
            record[4] = receipt_zones[i]
            record[3] = receipt_points[i]
            write_through_deliveries(record, info, file_writer, rows)

def search_through_combos(record, info, file_writer):
    global receipt_button_0
    global delivery_button_0 
    global receipt_button_1
    global delivery_button_1
    global receipt_clear
    global receipt_all
    global delivery_clear
    global delivery_all
    global apply_button
    global banner
    global driver
    for receipt in range(1, info[1] + 1):
        try_button(receipt_button_1)
        receipt_clear.click()
        list_item = driver.find_element(By.XPATH, f'//*[@id="section_1_control_31"]/div/div/div/label/div/div/ul/li[{receipt}]/a')
        record[4] = list_item.find_element(By.XPATH, f'//*[@id="section_1_control_31"]/div/div/div/label/div/div/ul/li[{receipt}]/a/span[1]').text
        list_item.click()
        receipt_button_1.click()
        driver.implicitly_wait(2)
        if info[4]:
            try_button(apply_button)
            try_button(banner)
            rows = extract_data()
            if not rows:
                continue
            zone_structures = list(set([row[-1] for row in rows]))
            if (len(zone_structures) == 1 and zone_structures[0] == "Entire System"):
                record[3] = receipt_button_0.get_attribute('title').replace(',', ' ')
                write_through_deliveries(record, info, file_writer, rows)
                continue
            
            for delivery in range(1, info[4] + 1):
                try_button(delivery_button_1)
                delivery_clear.click()
                list_item = driver.find_element(By.XPATH, f'//*[@id="section_1_control_37"]/div/div/div/label/div/div/ul/li[{delivery}]/a')
                record[6] = list_item.find_element(By.XPATH, f'//*[@id="section_1_control_37"]/div/div/div/label/div/div/ul/li[{delivery}]/a/span[1]').text
                list_item.click()
                delivery_button_1.click()
                
                try_button(apply_button)
                try_button(banner)
                rows = extract_data()
                record[5] = delivery_button_0.get_attribute('title').replace(',', ' ')
                record[3] = receipt_button_0.get_attribute('title').replace(',', ' ')
                if rows:
                    file_writer.writerows([record + row for row in rows])
            try_button(delivery_button_1)
            delivery_all.click()
            delivery_button_1.click()
                
        else:
            record[6] = 'NaN'
            try_button(apply_button)
            try_button(banner)
            rows = extract_data()
            record[5] = delivery_button_0.get_attribute('title').replace(',', ' ')
            record[3] = receipt_button_0.get_attribute('title').replace(',', ' ')
            if rows:
                file_writer.writerows([record + row for row in rows])
    try_button(receipt_button_1)
    receipt_all.click()
    receipt_button_1.click()
    
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

table = pd.read_csv("table2.csv")
pipelines = list(table["Pipeline"])
table = table.set_index("Pipeline")
dates = ['04/15/2018'] + [f"0{i}/01/2018" for i in range(5, 10)] + [f"0{i}/01/20{j}" for i in range(1, 10) for j in range(19, 23)] + [f"{i}/01/20{j}" for i in range(10, 13) for j in range(18, 23)]
for date in dates:
    date_mod = date.replace('/', '-')
    file = open(f'data/rate_data_{date_mod}.csv', 'w', newline = '')
    file_writer = csv.writer(file, delimiter = ',', quoting = csv.QUOTE_MINIMAL)
    file_writer.writerow(['Pipeline', 'Date', 'Rate Schedule', 'Receipt Point', 'Receipt Zone', 'Delivery Point', 'Delivery Zone', 'Tariff Rate Type', 'Tariff Rate', 'Magnitude', 'Tariff Rate Structure', 'Rate Zone'])

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
    receipt_all = driver.find_element(By.XPATH, '//*[@id="section_1_control_31"]/div/div/div/label/div/div/div[1]/div[3]/a[1]')
    delivery_clear = driver.find_element(By.XPATH, '//*[@id="section_1_control_37"]/div/div/div/label/div/div/div[1]/div[3]/a[2]')
    delivery_all = driver.find_element(By.XPATH, '//*[@id="section_1_control_37"]/div/div/div/label/div/div/div[1]/div[3]/a[1]')
    apply_button = driver.find_element(By.XPATH, '//*[@id="Apply_section_1_control_18"]')

    for pipeline in pipelines:
        record = [pipeline.replace(',', ' '), date] + [""]*5
        try_button(pipeline_button)
        pipeline_input.send_keys(pipeline)
        pipeline_input.send_keys(Keys.ENTER)
        time.sleep(1)
        info = list(table.loc[pipeline])
        for rate in range(1, info[0] + 1):
            try_button(rate_button)
            list_item = driver.find_element(By.XPATH, f'//*[@id="section_1_control_27"]/div/div/div/label/div/div/ul/li[{rate}]/a')
            record[2] = list_item.find_element(By.XPATH, f'//*[@id="section_1_control_27"]/div/div/div/label/div/div/ul/li[{rate}]/a/span[1]').text
            list_item.click()
            try_button(apply_button)
            try_button(banner)
            rows = extract_data()
            if not rows:
                continue

            if info[1]:
                zone_structures = list(set([row[-1] for row in rows]))
                if (len(zone_structures) == 1 and zone_structures[0] == "Entire System") or pipeline == 'Wyoming Interstate Company, L.L.C.':
                    write_through_receipts(record, info, file_writer, rows)
                else:
                    search_through_combos(record, info, file_writer)
            else:
                record[3] = receipt_button_0.get_attribute('title').replace(',', ' ')
                record[4] = 'NaN'
                record[5] = delivery_button_0.get_attribute('title').replace(',', ' ')
                record[6] = 'NaN'
                if rows:
                    file_writer.writerows([record + row for row in rows])          
            file.flush()
    file.close()