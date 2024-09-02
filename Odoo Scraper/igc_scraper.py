import time
import logging
import psutil
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

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

# Set up Chrome options
options = uc.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--user-data-dir=C:\\Users\\NeXbit\\AppData\\Local\\Google\\Chrome\\User Data")
options.add_argument("--headless")  # Run in headless mode
options.add_argument("--disable-gpu")  # Disable GPU acceleration

def IGCScraper(partNo):

    print("Searching part in IGC: " + partNo)   
    driver = uc.Chrome(options=options)
    url = 'https://importglasscorp.com/lookup'
    try:
        # Navigate to the URL
        driver.get(url)
        time.sleep(5)
        
        input = driver.find_element(By.ID, "search")
        input.send_keys(partNo + Keys.RETURN)
        time.sleep(5)

        table = driver.find_element(By.TAG_NAME, "table")
        a = table.find_element(By.TAG_NAME, "a")
        link = a.get_attribute("href")

        driver.get(link)

        table = driver.find_element(By.TAG_NAME, "table")
        tbody = table.find_element(By.TAG_NAME, "tbody")
        tr = tbody.find_element(By.TAG_NAME, "tr")

        td_elements = tr.find_elements(By.TAG_NAME, 'td')

        # Extract the values
        first_value = td_elements[0].find_element(By.TAG_NAME, 'a').text  # 1st value
        fourth_value = td_elements[3].find_element(By.TAG_NAME, 'b').text  # 4th value
        if td_elements[4].text == "In Stock":
            fifth_value = "Yes"
        else:
            fifth_value = "No"  # 5th value
        driver.quit()
        return "Part Number: " + first_value + "\nPrice: " + fourth_value + "\nIn Stock: " + fifth_value

    except:
        logger.error("Part number not found: " + partNo + " on IGC")
        driver.quit()
        return None

