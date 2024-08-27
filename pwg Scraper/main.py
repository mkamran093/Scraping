import os
import time
import json
import logging
import psutil
import pickle
import pyautogui
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

url = 'https://buypgwautoglass.com/PartSearch/search.asp?REG=&UserType=F&ShipToNo=85605&PB=544'
webdriver_path = "undetected_chromedriver.exe"

# Kill any existing Chrome driver processes
for proc in psutil.process_iter(['pid', 'name']):
    try:
        if 'chrome' in proc.info['name']:
            proc.kill()
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        pass

# Set up Chrome options
options = uc.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--user-data-dir=C:\\Users\\NeXbit\\AppData\\Local\\Google\\Chrome\\User Data")
options.add_argument("--headless")  # Run in headless mode
options.add_argument("--disable-gpu")  # Disable GPU acceleration

def searchPart(partNo, category):
    # Initialize the Chrome driver
    driver = uc.Chrome(options=options)
    try:
        # Navigate to the URL
        logger.info("Navigating to the URL: " + url)
        driver.get(url)

        # Wait for the element to be present
        wait = WebDriverWait(driver, 10)  # wait up to 10 seconds
        if category == "Auto Glass":
            type_select = wait.until(EC.presence_of_element_located((By.ID, "PartTypeA")))
        else:
            type_select = wait.until(EC.presence_of_element_located((By.ID, "PartTypeS")))

        type_select.click()
        part_no_input = driver.find_element(By.ID, "PartNo")

        # Send keys to the input field
        part_no_input.send_keys(partNo + Keys.RETURN)

        time.sleep(5)

        # Search for a p tag with text "No results found"
        try:
            no_results = driver.find_element(By.XPATH, "//p[contains(text(), 'No results found')]")
            logger.error("No results found for the part number: " + partNo)
            driver.quit()
            return
        except:
            pass

        # select the a tag which has the part number in its text
        part_link = driver.find_element(By.XPATH, "//a[contains(text(), '" + partNo + "')]")
        part_link.click()

        time.sleep(5)

        # Get the part details, search for table tag with id = productdetails and get the text of its p tag
        part_details = driver.find_element(By.ID, "productdetails").find_element(By.TAG_NAME, "p").text
        print(part_details)

        time.sleep(5)

        driver.quit()
    
    except TimeoutException:
        logger.error("The page took too long to load.")
        driver.quit()
        return


def main():
    print("===============================================")
    print("=====  Welcome to PGW Auto Glass Scraper  =====")
    print("===============================================")
    print("\n")

    partNo = input("Enter the part number: ")
    print("\n")
    print("1. Auto Glass    2. Sundry")
    category = input("Enter one option(1 or 2): ")

    while True:
        if category == '1' or category == '2':
            break
        else:
            print("Invalid input. Please enter a valid option.")
            category = input("Enter one option(1 or 2): ")
    
    print("\n")
    if category == '1':
        category = "Auto Glass"
    else:
        category = "Sundry"
    searchPart(partNo, category)

if __name__ == "__main__":
    main()
