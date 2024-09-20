from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
from requests.exceptions import RequestException
import csv
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
    chrome_options.add_argument("--remote-debugging-port=9222")  
    
    try:
        driver = uc.Chrome(options=chrome_options)
        return driver
    except Exception as e:
        logger.error(f"Error setting up Chrome driver: {str(e)}")
        raise

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

def extract_member_data(href, csv_writer):
    try:
        response = requests.get(href)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        soup = BeautifulSoup(response.content, 'html.parser')
        
        name_parts = soup.find("h2", {"class": "memberName"}).text.split()
        fName = name_parts[0]
        lName = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""
        
        data = soup.find_all("tr")
        
        office_link = data[0].find("a").get("href") if data[0].find("a") else 'N/A'
        company = data[0].find("a").text if data[0].find("a") else 'N/A'
        email = data[5].find("a").text if len(data) > 5 and data[5].find("a") else 'N/A'
        phone = data[2].text.split(":")[1].strip() if len(data) > 2 and ":" in data[2].text else 'N/A'
        address = ' '.join(data[0].find_all('td')[1].text.replace(company, "").strip().split()) if len(data[0].find_all('td')) > 1 else 'N/A'
        website = extract_url(office_link)

        row_data = [fName, lName, email, phone, address, company, website]
        csv_writer.writerow(row_data)
        logger.info(f"Data extracted and written for {fName} {lName}")
    
    except RequestException as e:
        logger.error(f"Request failed for {href}: {str(e)}")
    except IndexError as e:
        logger.error(f"IndexError while processing {href}: {str(e)}")
    except AttributeError as e:
        logger.error(f"AttributeError while processing {href}: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error while processing {href}: {str(e)}")


def search_members(text, driver, csv_writer):
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
            extract_member_data(href, csv_writer)
        except Exception as e:
            logger.error(f"Error extracting data from {href}: {str(e)}")

def main():
    driver = setup_driver()
    driver.get("https://bton.rapams.com/scripts/mgrqispi.dll?APPNAME=IMS&PRGNAME=IMSMemberLogin&ARGUMENTS=-ABTR&SessionType=N&ServiceName=OSRH&NotLogin=Y")

    with open('member_data.csv', 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['First Name', 'Last Name', 'Email', 'Phone', 'Address', 'Company', 'Website'])  # Header row

        for first in range(ord('o'), ord('z') + 1):
            for second in range(ord('a'), ord('z') + 1):
                text = chr(first) + chr(second)
                try:
                    search_members(text, driver, csv_writer)
                except Exception as e:
                    logger.error(f"Error searching for {text}: {str(e)}")
                driver.get("https://bton.rapams.com/scripts/mgrqispi.dll?APPNAME=IMS&PRGNAME=IMSMemberLogin&ARGUMENTS=-ABTR&SessionType=N&ServiceName=OSRH&NotLogin=Y")
        # for first in range(ord('j'), ord('z') + 1):
        #     try:
        #         search_members(f'n{chr(first)}', driver, csv_writer)
        #     except Exception as e:
        #         logger.error(f"Error searching for l{chr(first)}: {str(e)}")
        #     driver.get("https://bton.rapams.com/scripts/mgrqispi.dll?APPNAME=IMS&PRGNAME=IMSMemberLogin&ARGUMENTS=-ABTR&SessionType=N&ServiceName=OSRH&NotLogin=Y")
    driver.quit()

if __name__ == '__main__':
    main()