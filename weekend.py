from selenium import webdriver
from selenium.webdriver.chrome.service import Service

from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import logging
from selenium.webdriver.remote.remote_connection import LOGGER
from datetime import datetime, timedelta
import time
from login import username, password

def launchBrowser():
    chrome_options = Options()
    chrome_options.add_argument("start-maximized")
    chrome_options.add_experimental_option("detach", True)
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.get("https://dusk.backoffice.dutchie.com/reports/closing-report/registers")
    return driver

def login():
    wait = WebDriverWait(driver, 10)
    wait.until(EC.element_to_be_clickable((By.ID, "input-input_login-email"))).send_keys(username)
    wait.until(EC.element_to_be_clickable((By.ID, "input-input_login-password"))).send_keys(password)
    login_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".MuiButton-root.MuiButton-containedPrimary")))
    login_button.click()

def click_dropdown(): # This is to open store dropdown
    wait = WebDriverWait(driver, 10)
    dropdown_xpath = "/html/body/div[1]/div/div[1]/div[2]/div[2]/div"
    WebDriverWait(driver, 10).until(
        EC.invisibility_of_element_located((By.CSS_SELECTOR, "div.sc-ppyJt.jlHGrm"))
    )
    dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, dropdown_xpath)))
    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", dropdown)
    dropdown.click()

def store():
    wait = WebDriverWait(driver, 10)

    def select_dropdown_item(item_text):
        try:
            click_dropdown()
            xpath = f"//li[contains(text(), '{item_text}')]"
            item = wait.until(EC.visibility_of_element_located((By.XPATH, xpath)))
            item.click()
            return True
        except (TimeoutException, NoSuchElementException) as e:
            print(f"Error while trying to select '{item_text}' from the dropdown: {e}")
            return False

    for item_text in ["Buzz Cannabis - Mission Valley", "Buzz Cannabis-La Mesa"]:
        if not select_dropdown_item(item_text):
            break
        print("\n\033[1m" + item_text + "\033[0m\n")
        process()
        time.sleep(5)

    print("Completed processing all items.")

def click_date_input_field(driver):
    date_input_id = "input-input_"  # Adjust if necessary
    date_input = WebDriverWait(driver, 7).until(EC.element_to_be_clickable((By.ID, date_input_id)))
    date_input.click()

def get_last_three_days():
    today = datetime.now()
    last_three_days = [today - timedelta(days=i) for i in range(1, 4)]
    return [str(int(day.strftime('%d'))) for day in last_three_days]

def click_dates_in_calendar(driver, days_of_month):
    try:
        for day in days_of_month:
            day_div_xpath = f"//div[text()='{day}']"
            day_div = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, day_div_xpath)))
            click_element_with_js(driver, day_div)
            time.sleep(2)
        button = WebDriverWait(driver, 7).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Run')]")))
        button.click()
    except TimeoutException:
        print("Element not clickable.")

def click_element_with_js(driver, element):
    driver.execute_script("arguments[0].click();", element)

def extract_monetary_values(driver):
    css_selector = "[class$='table-cell-right-']"
    time.sleep(3)
    elements = WebDriverWait(driver, 35).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, css_selector))
    )
    monetary_values = []
    for element in elements[:3]:
        value_text = element.text
        try:
            numeric_value = float(value_text.replace('$', '').replace(',', '').replace('(', '-').replace(')', ''))
            monetary_values.append(numeric_value)
        except ValueError:
            print(f"Could not convert '{value_text}' to float.")
    return monetary_values

def process():
    days_of_month = get_last_three_days()
    for day in days_of_month:
        time.sleep(3)
        click_date_input_field(driver)
        click_dates_in_calendar(driver, [day])
        gross = extract_monetary_values(driver)
        formatted_date = (datetime.now() - timedelta(days=days_of_month.index(day) + 1)).strftime('%m/%d')
        if len(gross) >= 2:
            #print("--------------------------------")
            #print(f"{formatted_date} Sales was ${gross[0] + gross[1]}")
            #print()
            print("\033[1m--------------------------------\033[0m")
            print(f"\033[1m{formatted_date} {gross[0]} {gross[1]}\033[0m")
            print("\033[1m--------------------------------\033[0m")
            #print()
            print(float((-1 * gross[1]) / gross[0]))
            #print("--------------------------------")
        else:
            print("Not enough data to calculate the sum of sales.")

driver = launchBrowser()
login()
store()
driver.quit()
