from categories import scrape_sub_categories
import requests
from bs4 import BeautifulSoup
from base64 import b64decode
import logging
from constants import ZYTE_API_URL, ZYTE_API_KEY

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

categories_url = {
    "1": "https://www.wayfair.com/furniture/cat/furniture-c45974.html", 
    "2": "https://www.wayfair.com/outdoor/cat/outdoor-c32334.html",
    "3": "https://www.wayfair.com/bed-bath/cat/bed-bath-c215329.html", 
    "4": "https://www.wayfair.com/rugs/cat/rugs-c215385.html", 
    "5": "https://www.wayfair.com/decor-pillows/cat/decor-pillows-c45752.html", 
    "6": "https://www.wayfair.com/lighting/cat/lighting-c215735.html", 
    "7": "https://www.wayfair.com/storage-organization/cat/storage-organization-c215875.html", 
    "8": "https://www.wayfair.com/kitchen-tabletop/cat/kitchen-tabletop-c45667.html", 
    "9": "https://www.wayfair.com/baby-kids/cat/baby-kids-c45226.html", 
    "10": "https://www.wayfair.com/home-improvement/cat/home-improvement-c45342.html", 
    "11": "https://www.wayfair.com/appliances/cat/appliances-c215602.html", 
    "12": "https://www.wayfair.com/pet/cat/pet-c504273.html", 
    "13": "https://www.wayfair.com/holiday-decor/cat/holiday-decor-c1859601.html",
    "14": "https://www.wayfair.com/shop-by-room/cat/shop-by-room-c1876502.html"
}

def select_sub_category(url):
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
            sub_categories_name = []
            sub_categories = soup.find('div', {'data-cypress-id': 'subnavWrap'}).find_all('div', class_="CategoryLandingPageNavigation-linkWrap _1d89u260")
            for index, sub_category in enumerate(sub_categories, start=1):
                sub_categories_name.append(sub_category.find('p').get_text())
                url = sub_category.find('a', {'data-hb-id': 'Card'})['href']
                sub_categories_url[str(index)] = url
            
            formatted_string = ""
            max_length = max(len(sub_category) for sub_category in sub_categories_name)
            for i in range(0, len(sub_categories_name), 3):
                line = ""
                for j in range(3):
                    index = i + j
                    if index < len(sub_categories_name):
                        number = index + 1
                        name = sub_categories_name[index]
                        line += f"{number:2}. {name.ljust(max_length)}  "
                formatted_string += line.rstrip() + "\n"
            print(formatted_string)

            while True:
                sub_category = input("\nEnter number of the corresponding sub-sub-category to scrape: ")
                if sub_category in sub_categories_url:
                    logging.info(f"Selected sub-category: {sub_categories_name[int(sub_category)-1]}")
                    scrape_sub_categories(sub_categories_url[sub_category])
                    break
                else:
                    logging.warning(f"Invalid input: {sub_category}")
                    print("Invalid input. Please enter a valid number.")

    except requests.RequestException as e:
        logging.error(f"Network error when retrieving sub-categories: {e}")
    except ValueError as e:
        logging.error(f"Error parsing sub-categories: {e}")
    except Exception as e:
        logging.error(f"Unexpected error in select_sub_category: {e}")

def select_category(url):
    try:
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
        categories_name = []
        categories = soup.find('div', {'data-cypress-id': 'subnavWrap'})
        if not categories:
            raise ValueError("Could not find categories section")
        
        categories = categories.find_all('div', class_="CategoryLandingPageNavigation-linkWrap _1d89u260")
        for index, category in enumerate(categories, start=1):
            name = category.find('p').get_text()
            url = category.find('a', {'data-hb-id': 'Card'})['href']
            categories_name.append(name)
            categories_url[str(index)] = url
            
        formatted_string = ""
        max_length = max(len(category) for category in categories_name)
        for i in range(0, len(categories_name), 3):
            line = ""
            for j in range(3):
                index = i + j
                if index < len(categories_name):
                    number = index + 1
                    name = categories_name[index]
                    line += f"{number:2}. {name.ljust(max_length)}  "
            formatted_string += line.rstrip() + "\n"
        print(formatted_string)

        while True:
            category = input("\nEnter number of the corresponding sub-category to scrape: ")
            if category in categories_url:
                logging.info(f"Selected category: {categories_name[int(category)-1]}")
                select_sub_category(categories_url[category])
                break
            else:
                logging.warning(f"Invalid input: {category}")
                print("Invalid input. Please enter a valid number.")

    except requests.RequestException as e:
        logging.error(f"Network error when retrieving categories: {e}")
    except ValueError as e:
        logging.error(f"Error parsing categories: {e}")
    except Exception as e:
        logging.error(f"Unexpected error in select_category: {e}")
        
def main():
    print("Welcome to Wayfair Scraper!\n")
    print(" 1. Furniture          2. Outdoor              3. Bedding & Bath\n"
          " 4. Rugs               5. Decor & Pillows      6. Lighting\n"
          " 7. Organization       8. Kitchen              9. Baby & Kids\n"
          "10. Home Improvement  11. Appliances          12. Pet\n"
          "13. Holiday           14. Shop By Room\n")

    while True:
        category = input("\nEnter number of the corresponding category to scrape: ")
        if category in categories_url:
            logging.info(f"Selected main category: {category}")
            select_category(categories_url[category])
            break
        else:
            logging.warning(f"Invalid input: {category}")
            print("Invalid input. Please enter a valid number.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Script terminated by user.")
    except Exception as e:
        logging.error(f"Unhandled exception in main: {e}")