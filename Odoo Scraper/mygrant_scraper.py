import logging
import psutil
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

webdriver_path = "undetected_chromedriver.exe"

# Kill any existing Chrome driver processes
for proc in psutil.process_iter(['pid', 'name']):
    try:
        if 'chrome' in proc.info['name']:
            proc.kill()
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        pass


def MyGrantScraper(partNo):

    # Set up Chrome options
    options = uc.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--user-data-dir=C:\\Users\\NeXbit\\AppData\\Local\\Google\\Chrome\\User Data")
    options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--disable-gpu")  # Disable GPU acceleration
    driver = uc.Chrome(options=options)
    url = 'https://www.mygrantglass.com/pages/search.aspx?q=' + partNo + '&sc=B023&do=Search'

    try:
        logger.info("Searching part in MyGrant: " + partNo)
        driver.get(url)
        try:

            # Wait for the element to be present
            all_parts = []
            wait = WebDriverWait(driver, 5)
            location = wait.until(EC.presence_of_element_located((By.XPATH, "//span[@id='cpsr_LabelResultsHeader']"))).text.split("-")[1].strip()
            table = wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "table")))[1]
            products = table.find_elements(By.TAG_NAME, "tr")[1:]
            for product in products:
                part = [location]
                part.append(product.find_elements(By.TAG_NAME, "td")[1].text)
                part.append(product.find_elements(By.TAG_NAME, "td")[2].text)
                part.append(product.find_elements(By.TAG_NAME, "td")[3].text)
                all_parts.append(part)

            driver.quit()
            print(all_parts)
            return all_parts
        except NoSuchElementException:
            logger.error("Part number not found: " + partNo + " on MyGrant")
            driver.quit()
            return None

    except:
        logger.error("Part number not found: " + partNo + " on MyGrant")
        driver.quit()
        return None        
    

if __name__ == "__main__":
    MyGrantScraper("FW05322")