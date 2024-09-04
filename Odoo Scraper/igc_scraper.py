import logging
import psutil
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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

def IGCScraper(partNo):

    # Set up Chrome options
    options = uc.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--user-data-dir=C:\\Users\\NeXbit\\AppData\\Local\\Google\\Chrome\\User Data")
    options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--disable-gpu")  # Disable GPU acceleration
    print("Searching part in IGC: " + partNo)   
    driver = uc.Chrome(options=options)
    url = 'https://importglasscorp.com/glass/' + partNo
    try:
        # Navigate to the URL
        driver.get(url)

        # Wait for the tables to be present
        wait = WebDriverWait(driver, 10)  # wait up to 10 seconds
        table = wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
        location = table.find_element(By.XPATH, "./preceding-sibling::*[1]").find_element(By.TAG_NAME, 'b').text
        if location != "Opa-Locka":
            print("Part not available in Opa-Locka")
            driver.quit()
            return None

        tbody = table.find_element(By.TAG_NAME, "tbody")
        try:
            tr = tbody.find_element(By.TAG_NAME, "tr")
        except:
            print("Part number not found: " + partNo + " on IGC")

        td_elements = tr.find_elements(By.TAG_NAME, 'td')
        first_value = td_elements[0].find_element(By.TAG_NAME, 'a').text  # 1st value
        fourth_value = td_elements[3].find_element(By.TAG_NAME, 'b').text  # 4th value
        if td_elements[4].text == "In Stock":
            fifth_value = "Yes"
        else:
            fifth_value = "No"  # 5th value

        driver.quit()
        return {
            "part_number": first_value,
            "price1": fourth_value,
            "in_stock": fifth_value,
            "location": location
        }

    except:
        logger.error("Part number not found: " + partNo + " on IGC")
        driver.quit()
        return None

if __name__ == "__main__":
    IGCScraper("FW05322")