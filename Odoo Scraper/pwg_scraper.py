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



def searchPart(driver, partNo):
    try:
        # Navigate to the URL
        print("Searching part in PWG: " + partNo)
        driver.get(url)
        # Wait for the element to be present
        wait = WebDriverWait(driver, 10)  

        type_select = wait.until(EC.presence_of_element_located((By.ID, "PartTypeA")))
        type_select.click()
        part_no_input = wait.until(EC.presence_of_element_located((By.ID, "PartNo")))

        # Send keys to the input field
        part_no_input.send_keys(partNo + Keys.RETURN)

        parts = []
        location = wait.until(EC.presence_of_element_located((By.XPATH, "//span[@class='b2btext']"))).text.split(":: ")[1].strip()

        products = wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "table")))[2].find_elements(By.TAG_NAME, "tr")
        for product in products:
            part = []
            try:
                partName = product.find_element(By.XPATH, "//td[@class='partdesc']").find_element(By.TAG_NAME, "font").text
                if(partNo in partName):
                    part.append(partName)
                    description = product.find_element(By.XPATH, "//td[@class='partdesc']").find_element(By.XPATH, "//div[@class='options']")[1].text
                    part.append(description)
                    print(description)
                    check_button = wait.until(EC.presence_of_element_located((By.XPATH, "//button[@class='button check']")))
                    check_button.click()

                    try:
                        availability = product.find(EC.presence_of_element_located((By.XPATH, "//td[@ref-qty]"))).text
                    except:
                        availability = "Not available"
                    finally:
                        print(availability)
                        part.append(availability)
                else:
                    break
            except:
                continue
            part.append(location)
            print(part)
            parts.append(part)
        driver.quit()


        # Select the a tag which has the part number in its text
        # try:
        #     part_link = wait.until(EC.presence_of_element_located((By.XPATH, "//font[contains(text(), '" + partNo + "')]"))).text
        # except NoSuchElementException:
        #     logger.error("No results found for the part number: " + partNo)
        #     return
        
        # location = wait.until(EC.presence_of_element_located((By.XPATH, "//span[@class='b2btext']"))).text
        # # Check for first button with class = "button check"
        # try:
        #     check_button = wait.until(EC.presence_of_element_located((By.XPATH, "//button[@class='button check']")))
        #     check_button.click()
        # except NoSuchElementException:
        #     pass

        # # Search for a td tag with a property named "ref-qty" and get its text
        # try:
        #     ref_qty = wait.until(EC.presence_of_element_located((By.XPATH, "//td[@ref-qty]"))).text
        # except NoSuchElementException:
        #     ref_qty = "Not available"
        # print("Available quantity: " + ref_qty + "\nPart No: " + part_link + "\nLocation: " + location)
        # return "Available quantity: " + ref_qty + "\nPart No: " + part_link + "\nLocation: " + location
    except TimeoutException:
        logger.error("No results found for the part number: " + partNo + " on PWG.")
        return None

def PWGScraper(partNo):

    # Set up Chrome options
    options = uc.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--user-data-dir=C:\\Users\\NeXbit\\AppData\\Local\\Google\\Chrome\\User Data")
    options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--disable-gpu")  # Disable GPU acceleration
    driver = uc.Chrome(options=options)

    try:
        result = searchPart(driver, partNo)
        driver.quit()
        return result
    finally:
        driver.quit()

if __name__ == "__main__":
    PWGScraper("FW05322")
