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


def PilkingtonScraper(partNo):

    driver = uc.Chrome(options=options)
    url = 'https://shop.pilkington.com/ecomm/search/basic/?queryType=2&query=' + partNo + '&inRange=true&page=1&pageSize=30&sort=PopularityRankAsc'
    try:
        # Navigate to the URL
        logger.info("Searching part in Pilkington: " + partNo)
        driver.get(url)
        
        try:

            # Wait for the element to be present
            wait = WebDriverWait(driver, 10)  # wait up to 10 seconds
            part_no = wait.until(EC.presence_of_element_located((By.XPATH, "//span[@ng-if='!perm.canViewProdDetails']"))).text
            part_name = wait.until(EC.presence_of_element_located((By.XPATH, "//span[@class='description']"))).text
            price = wait.until(EC.presence_of_element_located((By.XPATH, "//span[@class='amount']"))).text

            driver.quit()
            return "Part Number: " + part_no + "\nPart Name: " + part_name + "\nPrice: " + price
        except NoSuchElementException:
            logger.error("Part number not found: " + partNo + " on Pilkington")
            driver.quit()
            return None

    except:
        logger.error("Part number not found: " + partNo + " on Pilkington")
        driver.quit()
        return None