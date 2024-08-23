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
    logging.info(f"Scraping product....")
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
            brand = json_data.get('brand', {}).get('name')
            review_count = json_data.get('aggregateRating', {}).get('reviewCount')
            rating_value = json_data.get('aggregateRating', {}).get('ratingValue')
            price = json_data.get('offers', {}).get('price')
            currency = json_data.get('offers', {}).get('priceCurrency')
            

            description = []
            div = soup.find('ul', class_="BulletList BulletList--withPadding")
            if div:
                for li in div.find_all('li'):
                    description.append(li.get_text(strip=True))
                    
            product_overview = []
            divs = soup.find('div', {'id': 'Pres_vizcon_visual::default'})
            if divs:
                for p in divs.find_all('p'):
                    product_overview.append(p.get_text(strip=True))

            availability = json_data.get('offers', {}).get('availability')
            in_stock = availability == "http://schema.org/InStock"

            img_section = soup.find('div', class_='ProductDetailImageCarousel-thumbnails ProductDetailImageCarousel-thumbnails--halfColumnWidthCarousel')
            urls = []
            for li in img_section.find_all('li'):
                urls.append(li.find('img')['src'])
            
            img_urls = []
            for url in urls:
                new_url = url.replace('resize-h56-w56%5Ecompr-r50', 'resize-h800-w800%5Ecompr-r85')
                img_urls.append(new_url)

            with open('product_data.csv', mode='a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)

                if os.path.getsize('product_data.csv') == 0:
                    writer.writerow([
                    'Product Name', 'Price', 'Currency', 'SKU', 'Brand', 'Category', 'Rating', 'Availability',
                    'Reviews', 'Product Description', 'Overview', 'Image URLs'
                ])

                writer.writerow([
                    product_name,
                    price,
                    currency,
                    sku,
                    brand,
                    category,
                    rating_value,
                    'In Stock' if in_stock else 'Out of Stock',
                    review_count,
                    str(description),
                    ' | '.join(product_overview),
                    ' | '.join(img_urls)
                ])

            logging.info(f"Product {product_name} scraped successfully")
    except Exception as e:
        logging.error(f"Failed to scrape product {product['name']}: {e}")

def scrape_sub_categories(name, url):
    logging.info(f"Scraping sub-category {name} ...")
    url = url + '?itemsperpage=96'
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

                all_products = []

                total_products_text = soup.find('div', {'data-enzyme-id': 'ResultsText'}).text
                total_products = int(re.sub(r'[^\d]', '', total_products_text))
                
                logging.info(f"Extracting prodcut urls.....")
                while len(all_products) < total_products:
                    print(len(soup.find_all('div', {'data-hb-id': 'ProductCard'})))
                    for product in soup.find_all('div', {'data-hb-id': 'ProductCard'}):
                        product_url = product.find('a', {'data-enzyme-id': 'BrowseProductCardWrapper-component'})['href']
                        all_products.append(product_url)
                        scrape_product(product_url, name)

                    next_page = soup.find('a', {'data-enzyme-id': 'paginationNextPageLink'})['href']
                    if next_page:
                        api_response = requests.post(
                            ZYTE_API_URL,
                            auth=(ZYTE_API_KEY, ""),
                            json={
                                "url": next_page,
                                "httpResponseBody": True,
                            },
                        )
                        if api_response.status_code == 200:
                            print('on next page')
                            http_response_body = b64decode(api_response.json()["httpResponseBody"])
                            soup = BeautifulSoup(http_response_body, 'html.parser')
                        else:
                            logging.error(f"Failed to retrieve the webpage. Status code: {api_response.status_code}")
                    else:
                        break
                
                for product in all_products:
                    scrape_product(product, name)
    except Exception as e:
        logging.error(f"Failed to scrape sub-category {name}: {e}")
        print(e)

def scrape_categories(soup):
   
    try:
        category_name = soup.find('div', class_='CategoryCarousel-title').get_text(strip=True)
        logging.info(f"Scraping category {category_name} ...")

        for item in soup.find_all('li', class_='CategoryCarousel-carouselItem'):
            sub_category_name = item.find('p', class_='CategoryCarousel-imageTitle').get_text(strip=True)
            sub_category_url = item.find('a', class_='CategoryCarousel-imageContainer')['href']

            scrape_sub_categories(sub_category_name, sub_category_url)
    except Exception as e:
        logging.error(f"Failed to scrape category: {e}")
