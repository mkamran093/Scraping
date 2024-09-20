import logging
from constants import ZYTE_API_URL, ZYTE_API_KEY
from bs4 import BeautifulSoup
from base64 import b64decode
import requests
import json
import csv
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def other_method(soup):
    data = {
        'name': 'N/A',
        'sku': 'N/A',
        'brand': {'name': 'N/A'},
        'image': 'N/A',
        'description': 'N/A',
        'aggregateRating': {'reviewCount': 'N/A', 'ratingValue': 'N/A'},
        'offers': {'price': 'N/A', 'priceCurrency': 'N/A', 'availability': 'undefined'}
    }

    data['name'] = soup.find('h1', {'data-hb-id': 'Heading'}).get_text(strip=True)
    # data['sku'] = soup.find('div', {'data-hb-id': 'ProductSKU'}).get_text(strip=True)
    data['brand']['name'] = soup.find('a', {'data-hb-id': 'Link'}).get_text(strip=True)
    data['image'] = soup.find('img', {'data-hb-id': 'FluidImage'})['srcset']
    data['description'] = soup.find('div', {'data-hb-id': 'Accordion'}).find('div', {'class': 'BoxV3'}).get_text(strip=True)
    data['aggregateRating']['reviewCount'] = soup.find('span', {'data-hb-id': 'Link'}).get_text(strip=True).split()[0]
    data['aggregateRating']['ratingValue'] = soup.find('p', {'data-rtl-id': 'reviewsHeaderReviewsAverage'}).get_text(strip=True)
    price = soup.find('span', {'data-test-id': 'PriceDisplay'}).get_text(strip=True)
    data['offers']['price'] = price[1:] if price[0] == '$' else price
    data['offers']['priceCurrency'] = price[0] if price[0] == '$' else 'N/A'

    return data



def scrape_product(product, category):
    csv_file = "products_data.csv"

    try:
        # Check if the product URL already exists in the CSV file
        if os.path.exists(csv_file):
            with open(csv_file, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row.get('Product Url') == product:
                        logging.info(f"Product URL {product} already exists in the CSV. Skipping.")
                        return

        logging.info(f"Scraping Product: {product}")
        api_response = requests.post(
            ZYTE_API_URL,
            auth=(ZYTE_API_KEY, ""),   
            json={
                "url": product,
                "httpResponseBody": True,
            },
        )
        api_response.raise_for_status()

        if (api_response.status_code == 520):
            logging.error(f"Error 520: Web server is returning an unknown error for product {product}")
            scrape_product(product, category)
            return
        http_response_body = b64decode(api_response.json()["httpResponseBody"])
        soup = BeautifulSoup(http_response_body, 'html.parser')
        
        # Find the JSON-LD script tag
        script_tag = soup.find('script', type='application/ld+json')
        
        if not script_tag or len(script_tag) < 5:
            json_data = other_method(soup)
        else:
            # Parse the JSON content
            json_data = json.loads(script_tag.string)
        
        # Extract the desired information
        product_name = json_data.get('name', 'N/A')
        sku = json_data.get('sku', 'N/A')
        brand_name = json_data.get('brand', {}).get('name', 'N/A')
        image_url = json_data.get('image', 'N/A')
        description = json_data.get('description', 'N/A')
        review_count = json_data.get('aggregateRating', {}).get('reviewCount', 'N/A')
        rating = json_data.get('aggregateRating', {}).get('ratingValue', 'N/A')
        price = json_data.get('offers', {}).get('price', 'N/A')
        price_currency = json_data.get('offers', {}).get('priceCurrency', 'N/A')
        availability = json_data.get('offers', {}).get('availability', 'N/A')
        
        product_overview = []
        divs = soup.find('div', {'id': 'Pres_vizcon_visual::default'})
        if divs:
            for p in divs.find_all('p'):
                product_overview.append(p.get_text(strip=True))

        in_stock = availability == "http://schema.org/InStock"

        img_section = soup.find('div', class_='ProductDetailImageCarousel-thumbnails ProductDetailImageCarousel-thumbnails--halfColumnWidthCarousel')
        img_urls = []
        if img_section:
            urls = [li.find('img')['src'] for li in img_section.find_all('li')]
            img_urls = [url.replace('resize-h56-w56%5Ecompr-r50', 'resize-h800-w800%5Ecompr-r85') for url in urls]
        else:
            logging.warning("No images found for product")

        with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)

            if os.path.getsize(csv_file) == 0:
                writer.writerow([
                'Product Name', 'Price', 'Currency', 'SKU', 'Brand', 'Category', 'Rating', 'Availability',
                'Reviews', 'Product Description', 'Overview', 'Product Url', 'Image', 'Image URLs'
            ])

            writer.writerow([
                product_name, price, price_currency, sku, brand_name, category,
                rating, 'In Stock' if in_stock else 'Out of Stock', review_count,
                description, ' | '.join(product_overview), product, image_url,
                ' | '.join(img_urls)
            ])

        logging.info(f"Product {product_name} scraped successfully")

    except requests.RequestException as e:
        logging.error(f"Network error when scraping product {product}: {e}")
    except json.JSONDecodeError as e:
        logging.error(f"Error parsing JSON data for product {product}: {e}")
    except ValueError as e:
        logging.error(str(e))
    except Exception as e:
        logging.error(f"Unexpected error when scraping product {product}: {e}")

def scrape_sub_categories(url):
    try:
        logging.info(f"Scraping sub-category: {url}")
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

        try:
            heading = soup.find('h1', {'data-hb-id': 'Heading'})
            heading_text = heading.get_text(strip=True)
        except AttributeError:
            heading = 'N/A'
        logging.info(f'Scraping Sub-Category: {heading_text}')

        while True:
            products = soup.find_all('div', {'data-hb-id': 'Grid.Item'})
            for product in products:
                product_url = product.find('a')['href']
                scrape_product(product_url, heading_text)

            next_page = soup.find('a', {'data-enzyme-id': 'paginationNextPageLink'})
            if not next_page:
                logging.info("Reached last page of sub-category")
                break

            next_page_url = next_page['href']
            logging.info(f"Moving to next page: {next_page_url}")
            api_response = requests.post(
                ZYTE_API_URL,
                auth=(ZYTE_API_KEY, ""),
                json={
                    "url": next_page_url,
                    "httpResponseBody": True,
                },
            )
            api_response.raise_for_status()
            http_response_body = b64decode(api_response.json()["httpResponseBody"])
            soup = BeautifulSoup(http_response_body, 'html.parser')

    except requests.RequestException as e:
        logging.error(f"Network error when scraping sub-category {url}: {e}")
    except ValueError as e:
        logging.error(str(e))
    except Exception as e:
        logging.error(f"Unexpected error when scraping sub-category {url}: {e}")
