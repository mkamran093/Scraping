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

def searchPart(driver, partNo, category):
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
        # try:
        #     if driver.find_element(By.XPATH, "//p[contains(text(), 'No results found')]") is not None:
        #         logger.error("No results found for the part number: " + partNo)
        #         return
        # except:
        #     pass

        # Select the a tag which has the part number in its text
        try:
            part_link = driver.find_element(By.XPATH, "//a[contains(text(), '" + partNo + "')]")
        except NoSuchElementException:
            logger.error("No results found for the part number: " + partNo)
            return
        
        # Check for first button with class = "button check"
        try:
            check_button = driver.find_element(By.XPATH, "//button[@class='button check']")
            check_button.click()
        except NoSuchElementException:
            pass

        time.sleep(5)

        # Search for a td tag with a property named "ref-qty" and get its text
        try:
            ref_qty = driver.find_element(By.XPATH, "//td[@ref-qty]").text
        except NoSuchElementException:
            ref_qty = "Not available"

        part_link.click()

        time.sleep(5)

        # Get the part details, search for table tag with id = productdetails and get the text of its p tag
        part_details = driver.find_element(By.ID, "productdetails").find_element(By.TAG_NAME, "p").text
        print("Available quantity: " + ref_qty)
        print(part_details)

        time.sleep(5)

    except TimeoutException:
        logger.error("The page took too long to load.")

def main():

    # Initialize the Chrome driver
    driver = uc.Chrome(options=options)

    print("\n")
    print("===============================================")
    print("=====  Welcome to PGW Auto Glass Scraper  =====")
    print("===============================================")
    print("\n")

    try:
        while True:
            partNo = input("Enter the part number: ")
            print("\n")
            print("1. Auto Glass    2. Sundry")
            category = input("Enter one option (1 or 2): ")

            while category not in ['1', '2']:
                print("Invalid input. Please enter a valid option.")
                category = input("Enter one option (1 or 2): ")

            category = "Auto Glass" if category == '1' else "Sundry"

            searchPart(driver, partNo, category)

            # Ask if the user wants to search for another part
            another_search = input("\nDo you want to search for another part? (yes/no): ").strip().lower()
            if another_search != 'yes':
                break

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
