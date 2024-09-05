import logging
import psutil
import undetected_chromedriver as uc
from bs4 import BeautifulSoup


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
    url = 'https://www.mygrantglass.com/pages/search.aspx?q=' + partNo + '&sc=r&do=Search'
    parts = []
    try:
        logger.info("Searching part in MyGrant: " + partNo)
        driver.get(url)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        driver.quit()
        try:
            div = soup.find('div', {'id': 'cpsr_DivParts'})
            locations = div.find_all('h3')[1:]
            tables = div.find_all('tbody')
            for table in tables:
                rows = table.find_all('tr')[1:]
                for row in rows:
                    data = row.find_all('td')[1:]
                    part = [data[1].find('a').text.replace('\n', '').strip(), data[2].text.replace('\n', '').strip(), data[0].find('span').text.replace('\n', '').strip(), locations[0].text.split(' - ')[0].strip()]
                    parts.append(part)
                locations.pop(0)
            print(parts)
            return parts
        except:
            print("not found")
            return None
    except:
        logger.error("Part number not found: " + partNo + " on MyGrant")
        return None        
    

if __name__ == "__main__":
    MyGrantScraper("5322")