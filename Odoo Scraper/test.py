import psutil
import time
import logging
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

for proc in psutil.process_iter(['pid', 'name']):
        try:
            if 'chrome' in proc.info['name']:
                proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

webdriver_path = "undetected_chromedriver.exe"

options = uc.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--user-data-dir=C:\\Users\\NeXbit\\AppData\\Local\\Google\\Chrome\\User Data")
# options.add_argument("--headless")  # Run in headless mode
options.add_argument("--disable-gpu")  # Disable GPU acceleration  
driver = uc.Chrome(options=options)

def searchPart(partNo):

    url = 'https://buypgwautoglass.com/PartSearch/search.asp?REG=&UserType=F&ShipToNo=85605&PB=544'
    try:
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
        
        products = wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "table")))[2].find_elements(By.TAG_NAME, "tr")[2:]
        wait.until(EC.presence_of_element_located((By.XPATH, "//button[@class='button check']"))).click()
        for product in products:
            part = []
            try:
                partName = product.find_elements(By.TAG_NAME, 'font')[1].text
                if (partNo in partName):
                    part.append(partName)
                    description = product.find_element(By.XPATH, "//div[@class='options']").text.replace('»', '').strip()
                    part.append(description)
                    try:
                        availability = product.find_element(By.XPATH, "//td[@ref-qty]").text
                        part.append(availability)
                    except NoSuchElementException:
                        part.append("Not available")
                    print(product.find_elements(By.TAG_NAME, 'font')[2].text)
                    part.append(location)
                    parts.append(part)
                else:
                    break
            except:
                continue
        
        ## Perfect above this line

        wait.until(EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Check Other Locations')]"))).click()

        try:
            matching_table = driver.find_element(By.XPATH, "//table[.//td//span[contains(text(), 'Branch:: MIAMI FL')]]")
        except:
            logger.info("Parts for Miami not found")
            return parts

        products = matching_table.find_elements(By.TAG_NAME, "tr")[2:]
        for product in products:
            part = []
            try:
                data = product.find_elements(By.TAG_NAME, 'font')
                partName = data[2].text
                if (partNo in partName):
                    part.append(partName)
                    description = product.find_element(By.XPATH, "//div[@class='options']").text.replace('»', '').strip()
                    part.append(description)
                    try:
                        availability = data[1].text
                        part.append(availability)
                    except NoSuchElementException:
                        part.append("Not available")
                    print(data[3].text)
                    part.append("Miami FL")
                    parts.append(part)
            except:
                continue
        return parts

    except TimeoutException:
        logger.error("No results found for the part number: " + partNo + " on PWG.")
        return None

def PWGScraper(partNo):

    try:
        result = searchPart(partNo)
        return result
    except:
        return None

if __name__ == "__main__":
    PWGScraper("DW01256")
