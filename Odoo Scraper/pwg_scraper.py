import time
import logging
import psutil
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
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

def searchPart(driver, partNo):
    try:
        # Navigate to the URL
        print("Searching part in PWG: " + partNo)
        driver.get(url)

        # Wait for the element to be present
        wait = WebDriverWait(driver, 10)  # wait up to 10 seconds
        type_select = wait.until(EC.presence_of_element_located((By.ID, "PartTypeA")))
        type_select.click()
        part_no_input = driver.find_element(By.ID, "PartNo")

        # Send keys to the input field
        part_no_input.send_keys(partNo + Keys.RETURN)

        time.sleep(5)

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
        return "Available quantity: " + ref_qty + "\n" + part_details

    except TimeoutException:
        logger.error("No results found for the part number: " + partNo + "on PWG.")
        return None

def PWGScraper(partNo):

    driver = uc.Chrome(options=options)

    try:
        result = searchPart(driver, partNo)
        driver.quit()
        return result
    finally:
        driver.quit()
