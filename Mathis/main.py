from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
import psutil
import logging
import requests

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

all_data = []

for proc in psutil.process_iter(['pid', 'name']):
    try:
        if 'chrome' in proc.info['name'].lower():
            proc.kill()
            logger.info(f"Killed Chrome process: {proc.info['pid']}")
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
        logger.error(f"Error killing Chrome process: {e}")


def setup_driver():
    # set up driver
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = uc.Chrome(options=chrome_options)
    return driver

def extract_url(link):
    try:
        response = requests.get(f"https://bton.rapams.com/{link}")
        soup = BeautifulSoup(response.content, 'html.parser')
        url = soup.find_all("tr")[-1]
        if ("Web Page" in url.text):
            return url.find("a").text
        else:
            return 'N/A'
    except:
        print(f"Error extracting url from {link}")
        return 'N/A'

def extract_member_data(href):
    response = requests.get(href)
    soup = BeautifulSoup(response.content, 'html.parser')
    fName, lName = soup.find("h2", {"class": "memberName"}).text.split(" ")
    data = soup.find_all("tr")
    try:
        office_link = data[0].find("a").get("href")
    except:
        office_link = 'N/A'
    try:
        company = data[0].find("a").text
    except:
        company = 'N/A'
    try:
        email = data[5].find("a").text
    except:
        email = 'N/A'
    try:
        phone = data[2].text.split(":")[1].strip()
    except:
        phone = 'N/A'
    try:
        address = data[0].find_all('td')[1].text.replace(company, "").strip().replace("\n", " ")
    except:
        address = 'N/A'
    website = extract_url(office_link)

    print(fName, lName, email, phone, address, company, website)


def search_members(text, driver):
    wait = WebDriverWait(driver, 10)

    wait.until(EC.presence_of_element_located((By.ID, "rapAgentNickname"))).send_keys(text + Keys.RETURN)

    try:
        members = wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "tr")))[1:]
    except:
        print(f"No members found for {text}")
        return

    href_list = []
    for member in members:
        try:
            a_tag = member.find_element(By.XPATH, "./td[1]/a")
            href = a_tag.get_attribute("href")
            href_list.append(href)
        except:
            continue

    for href in href_list:
        try:
            extract_member_data(href)
        except:
            print(f"Error extracting data from {href}")
            continue

def main():
    driver = setup_driver()
    driver.get("https://bton.rapams.com/scripts/mgrqispi.dll?APPNAME=IMS&PRGNAME=IMSMemberLogin&ARGUMENTS=-ABTR&SessionType=N&ServiceName=OSRH&NotLogin=Y")

    for first in range(ord('a'), ord('z') + 1):
        for second in range(ord('a'), ord('z') + 1):
            text = chr(first) + chr(second)
            try:
                search_members(text, driver)
            except:
                print(f"Error searching for {text}")
                continue
            driver.get("https://bton.rapams.com/scripts/mgrqispi.dll?APPNAME=IMS&PRGNAME=IMSMemberLogin&ARGUMENTS=-ABTR&SessionType=N&ServiceName=OSRH&NotLogin=Y")
    

if __name__ == '__main__':
    main()