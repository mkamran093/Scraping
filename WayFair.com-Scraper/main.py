from categories import scrape_sub_categories
import requests
from bs4 import BeautifulSoup
from base64 import b64decode
import logging
from constants import ZYTE_API_URL, ZYTE_API_KEY

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
            sub_category = input("\nEnter number of the corresponding sub-sub-category to scrape: ")  
            while True:
                if sub_category in sub_categories_url:
                    break
                else:
                    sub_category = input("Invalid input. Please enter a valid number.") 
            scrape_sub_categories(sub_categories_url[sub_category])
    except:
        logging.error(f"Failed to retrieve the webpage. Status code: {api_response.status_code}")

def select_category(url):
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

            categories_url = {}
            categories_name = []
            categories = soup.find('div', {'data-cypress-id': 'subnavWrap'}).find_all('div', class_="CategoryLandingPageNavigation-linkWrap _1d89u260")
            for index, category in enumerate(categories, start=1):
                categories_name.append(category.find('p').get_text())
                url = category.find('a', {'data-hb-id': 'Card'})['href']
                categories_url[str(index)] = url
            
            formatted_string = ""
            max_length = max(len(category) for category in categories_name)  # Find the maximum length of category names

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
            category = input("\nEnter number of the corresponding sub-category to scrape: ")
            while True:
                if category in categories_url:
                    break
                else:
                    category = input("Invalid input. Please enter a valid number.")
            select_sub_category(categories_url[category])

    except:
        logging.error(f"Failed to retrieve the webpage. Status code: {api_response.status_code}")


def main():
    print("Welcome to Wayfair Scraper!\n")
    print(" 1. Furniture          2. Outdoor              3. Bedding & Bath\n"
          " 4. Rugs               5. Decor & Pillows      6. Lighting\n"
          " 7. Organization       8. Kitchen              9. Baby & Kids\n"
          "10. Home Improvement  11. Appliances          12. Pet\n"
          "13. Holiday           14. Shop By Room\n")

    category = input("\nEnter number of the corresponding category to scrape: ")

    

    while True:
        if category in categories_url:
            break
        else:
            category = input("Invalid input. Please enter a valid number.")
    select_category(categories_url[category])

if __name__ == "__main__":
    main()
