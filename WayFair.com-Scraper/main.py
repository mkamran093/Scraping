from categories import scrape_sub_categories
import requests
from bs4 import BeautifulSoup
from base64 import b64decode
import logging
from constants import ZYTE_API_URL, ZYTE_API_KEY
import json
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# categories_url: {
#     "1": "https://www.wayfair.com/furniture/cat/furniture-c45974.html", 
#     "2": "https://www.wayfair.com/outdoor/cat/outdoor-c32334.html",
#     "3": "https://www.wayfair.com/bed-bath/cat/bed-bath-c215329.html", 
#     "4": "https://www.wayfair.com/rugs/cat/rugs-c215385.html", 
#     "5": "https://www.wayfair.com/decor-pillows/cat/decor-pillows-c45752.html", 
#     "6": "https://www.wayfair.com/lighting/cat/lighting-c215735.html", 
#     "7": "https://www.wayfair.com/storage-organization/cat/storage-organization-c215875.html", 
#     "8": "https://www.wayfair.com/kitchen-tabletop/cat/kitchen-tabletop-c45667.html", 
#     "9": "https://www.wayfair.com/baby-kids/cat/baby-kids-c45226.html", 
#     "10": "https://www.wayfair.com/home-improvement/cat/home-improvement-c45342.html", 
#     "11": "https://www.wayfair.com/appliances/cat/appliances-c215602.html", 
#     "12": "https://www.wayfair.com/pet/cat/pet-c504273.html", 
#     "13": "https://www.wayfair.com/holiday-decor/cat/holiday-decor-c1859601.html",
#     "14": "https://www.wayfair.com/shop-by-room/cat/shop-by-room-c1876502.html"
# }

def load_json_data(filename='data.json'):
    if os.path.exists(filename):
        try:
            with open(filename, 'r') as file:
                content = file.read()
                if content.strip():  # Check if file is not empty
                    return json.loads(content)
                else:
                    logging.warning(f"File {filename} is empty. Returning empty dictionary.")
                    return {}
        except json.JSONDecodeError as e:
            logging.error(f"Error decoding JSON from {filename}: {e}")
            return {}
    else:
        logging.info(f"File {filename} not found. Returning empty dictionary.")
        return {}

def save_json_data(data, filename='data.json'):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=2)

def select_sub_category(url):

    data = load_json_data()
    sub_categories_url = data.get('sub_categories_url', {})

    if not sub_categories_url:
        try:
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

                sub_categories_url = {}
                sub_categories = soup.find('div', {'data-cypress-id': 'subnavWrap'}).find_all('div', class_="CategoryLandingPageNavigation-linkWrap _1d89u260")
                for sub_category in sub_categories:
                    url = sub_category.find('a', {'data-hb-id': 'Card'})['href']
                    sub_categories_url[sub_category.find('p').get_text()] = url

        except requests.RequestException as e:
            logging.error(f"Network error when retrieving sub-categories: {e}")
        except ValueError as e:
            logging.error(f"Error parsing sub-categories: {e}")
        except Exception as e:
            logging.error(f"Unexpected error in select_sub_category: {e}")

    try:
        while sub_categories_url:
            key, url = sub_categories_url.popitem()
            scrape_sub_categories(url)
            data['sub_categories_url'] = sub_categories_url
            save_json_data(data)
    except Exception as e:
        logging.error(f"Error scraping sub-categories: {e}")
                

def select_category(url):

    data = load_json_data('data.json')
    categories_url = data.get('categories_url', {})

    try:
        
        if not categories_url:
            logging.info(f"Selecting category from URL: {url}")
            api_response = requests.post(
                ZYTE_API_URL,
                auth=(ZYTE_API_KEY, ""),
                json={
                    "url": url,
                    "httpResponseBody": True,
                },
            )
            api_response.raise_for_status()

            http_response_body = b64decode(api_response.json()["httpResponseBody"])
            soup = BeautifulSoup(http_response_body, 'html.parser')

            categories_url = {}
            categories = soup.find('div', {'data-cypress-id': 'subnavWrap'})
            if not categories:
                raise ValueError("Could not find categories section")
        
            categories = categories.find_all('div', class_="CategoryLandingPageNavigation-linkWrap _1d89u260")
            for category in categories:
                name = category.find('p').get_text()
                url = category.find('a', {'data-hb-id': 'Card'})['href']
                categories_url[name] = url

        while categories_url:
            key, url = categories_url.popitem()
            select_sub_category(url)
            data['categories_url'] = categories_url
            save_json_data(data)


    except requests.RequestException as e:
        logging.error(f"Network error when retrieving categories: {e}")
    except ValueError as e:
        logging.error(f"Error parsing categories: {e}")
    except Exception as e:
        logging.error(f"Unexpected error in select_category: {e}")

def main():
    print("Welcome to Wayfair Scraper!")
    print("Scraping has started")

    data = load_json_data('data.json')
    major_categories_url = data.get('major_categories_url', {})
    
    while major_categories_url:
        key, url = major_categories_url.popitem()
        select_sub_category(url)
        data['major_categories_url'] = major_categories_url
        save_json_data(data)
        

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Script terminated by user.")
    except Exception as e:
        logging.error(f"Unhandled exception in main: {e}")