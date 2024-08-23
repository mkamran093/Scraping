from constants import ZYTE_API_URL, ZYTE_API_KEY
from bs4 import BeautifulSoup
from base64 import b64decode
import requests
import logging
import json
import csv
import re
import os

def scrape_product(product, category):
    csv_file = category + '_products_data.csv'

    # Check if the product URL already exists in the CSV file
    if os.path.exists(csv_file):
        with open(csv_file, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row.get('Product Url') == product:
                    print(f"Product URL {product} already exists in the CSV. Skipping.")
                    return

    print("Scraping Product...")
    try:

        api_response = requests.post(
            ZYTE_API_URL,
            auth=(ZYTE_API_KEY, ""),   
            json={
                "url": product,
                "httpResponseBody": True,
            },
        )

        if api_response.status_code == 200:
            http_response_body = b64decode(api_response.json()["httpResponseBody"])
            soup = BeautifulSoup(http_response_body, 'html.parser')
            
             # Find the JSON-LD script tag
            script_tag = soup.find('script', type='application/ld+json')
            
            if script_tag:
                # Parse the JSON content
                json_data = json.loads(script_tag.string)
            
                # Extract the desired information
                product_name = json_data.get('name')
                sku = json_data.get('sku')
                brand_name = json_data.get('brand', {}).get('name')
                image_url = json_data.get('image')
                description = json_data.get('description')
                review_count = json_data.get('aggregateRating', {}).get('reviewCount')
                rating = json_data.get('aggregateRating', {}).get('ratingValue')
                price = json_data.get('offers', {}).get('price')
                price_currency = json_data.get('offers', {}).get('priceCurrency')
                availability = json_data.get('offers', {}).get('availability')
                    
                product_overview = []
                divs = soup.find('div', {'id': 'Pres_vizcon_visual::default'})
                if divs:
                    for p in divs.find_all('p'):
                        product_overview.append(p.get_text(strip=True))

                in_stock = availability == "http://schema.org/InStock"

                img_section = soup.find('div', class_='ProductDetailImageCarousel-thumbnails ProductDetailImageCarousel-thumbnails--halfColumnWidthCarousel')
                urls = []
                img_urls = []
                if (img_section):
                    for li in img_section.find_all('li'):
                        urls.append(li.find('img')['src'])
                    
                    for url in urls:
                        new_url = url.replace('resize-h56-w56%5Ecompr-r50', 'resize-h800-w800%5Ecompr-r85')
                        img_urls.append(new_url)
                else:
                    print("no images found")
    
                with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)

                    if os.path.getsize(csv_file) == 0:
                        writer.writerow([
                        'Product Name', 'Price', 'Currency', 'SKU', 'Brand', 'Category', 'Rating', 'Availability',
                        'Reviews', 'Product Description', 'Overview', 'Product Url', 'Image', 'Image URLs'
                    ])

                    writer.writerow([
                        product_name,
                        price,
                        price_currency,
                        sku,
                        brand_name,
                        category,
                        rating,
                        'In Stock' if in_stock else 'Out of Stock',
                        review_count,
                        description,
                        ' | '.join(product_overview),
                        product,
                        image_url,
                        ' | '.join(img_urls)
                    ])

            logging.info(f"Product {product_name} scraped successfully")
    except Exception as e:
        logging.error(f"Failed to scrape product {product['name']}: {e}")

def scrape_sub_categories(url):
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
                logging.info("Successfully retrieved and parsed the webpage content")

                heading = soup.find('h1', {'data-hb-id': 'Heading'}).get_text(strip=True)
                print('Scraping Sub-Category:', heading)

                logging.info(f"Extracting prodcut urls.....")
                while True:
                    for product in soup.find_all('div', {'data-hb-id': 'Card'}):
                        product_url = product.find('a')['href']
                        scrape_product(product_url, heading)

                    try:
                        next_page = soup.find('a', {'data-enzyme-id': 'paginationNextPageLink'})['href']
                        api_response = requests.post(
                            ZYTE_API_URL,
                            auth=(ZYTE_API_KEY, ""),
                            json={
                                "url": next_page,
                                "httpResponseBody": True,
                            },
                        )
                        if api_response.status_code == 200:
                            http_response_body = b64decode(api_response.json()["httpResponseBody"])
                            soup = BeautifulSoup(http_response_body, 'html.parser')
                        else:
                            logging.error(f"Failed to retrieve the webpage. Status code: {api_response.status_code}")
                            break
                           
                    except:
                        break
    except Exception as e:
        logging.error(f"Failed to scrape sub-category {heading}: {e}")
        print(e)

# def scrape_category(name, url):
#     logging.info(f"Scraping category {name} ...")
#     try:
#         api_response = requests.post(
#             ZYTE_API_URL,
#             auth=(ZYTE_API_KEY, ""),
#             json={
#                 "url": url,
#                 "httpResponseBody": True,
#             },
#         )
#         if api_response.status_code == 200:
#             http_response_body = b64decode(api_response.json()["httpResponseBody"])
#             soup = BeautifulSoup(http_response_body, 'html.parser')
#             logging.info("Successfully retrieved and parsed the webpage content")
#         for item in soup.find_all('div', class_='CategoryLandingPageNavigation-linkWrap _1d89u260'):
#             sub_category_url = item.find('a')['href']

#             scrape_sub_categories(sub_category_url)
#     except Exception as e:
#         logging.error(f"Failed to scrape category: {e}")

# def scrape_categories(soup):
#     try:
#         for item in soup.find_all('div', class_='CategoryLandingPageNavigation-linkWrap _1d89u260'):
#             category_name = item.find('p', {'data-hb-id': 'Text'}).get_text(strip=True)
#             category_url = item.find('a')['href']

#             scrape_category(category_name, category_url)
#     except Exception as e:
#         logging.error(f"Failed to scrape category: {e}")
