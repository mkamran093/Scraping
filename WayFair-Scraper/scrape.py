import requests
from bs4 import BeautifulSoup
from base64 import b64decode
import logging
from categories import scrape_categories
from constants import ZYTE_API_URL, ZYTE_API_KEY

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def start_scraping(url):
    for i in range(10):  
        try:
            logging.info(f"Attempt {i+1}: Scraping {url} using Zyte API")
            api_response = requests.post(
                ZYTE_API_URL,
                auth=(ZYTE_API_KEY, ""),
                json={
                    "url": url,
                    "httpResponseBody": True,
                },
            )

            if api_response.status_code == 200:
                http_response_body = b64decode(api_response.json()["httpResponseBody"])
                soup = BeautifulSoup(http_response_body, 'html.parser')
                logging.info("Successfully retrieved and parsed the webpage content")

                scrape_categories(soup)

                h2_tags = soup.find_all('h2')
                for tag in h2_tags:
                    print(tag.get_text())
                break  # Exit the loop if successful

            else:
                logging.error(f"Failed to retrieve the webpage. Status code: {api_response.status_code}")
        
        except requests.exceptions.RequestException as e:
            logging.error(f"Request failed: {e}")

        if i == 9:
            logging.critical(f"All attempts failed. Unable to scrape {url}")
