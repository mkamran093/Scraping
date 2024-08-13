import os
import requests
import base64
import json
from pymongo import MongoClient
from woocommerce import API
from dotenv import load_dotenv
import warnings
from cryptography.utils import CryptographyDeprecationWarning
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from colory.color import Color
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

# Suppress the CryptographyDeprecationWarning
warnings.filterwarnings("ignore", category=CryptographyDeprecationWarning)

# Load environment variables
load_dotenv()

# MongoDB Configuration
mongo_uri = os.getenv("MONGO_URI")
mongo_db_name = os.getenv("MONGO_DB_NAME")
mongo_collection_name = "products"
mongo_images_collection_name = "images"

assert mongo_uri, "MONGO_URI is not set"
assert mongo_db_name, "MONGO_DB_NAME is not set"

logging.info(f"Using MongoDB Database: {mongo_db_name}")
logging.info(f"Using MongoDB Collection: {mongo_collection_name}")

mongo_client = MongoClient(mongo_uri)
db = mongo_client[mongo_db_name]
collection = db[mongo_collection_name]
images_collection = db[mongo_images_collection_name]

# WooCommerce API Configuration
wcapi = API(
    url=os.getenv("WOOCOMMERCE_URL"),
    consumer_key=os.getenv("WOOCOMMERCE_CONSUMER_KEY"),
    consumer_secret=os.getenv("WOOCOMMERCE_CONSUMER_SECRET"),
    version="wc/v3"
)

def requests_retry_session(retries=5, backoff_factor=0.5, status_forcelist=(500, 502, 504), session=None):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

def upload_image_from_url_to_wordpress(image_url):
    existing_image = images_collection.find_one({"url": image_url})
    if existing_image:
        logging.info(f"Image already exists with ID: {existing_image['id']}")
        return existing_image['id']
    
    wp_url = os.getenv('WP_URL')
    wp_user = os.getenv('WP_USER')
    wp_app_password = os.getenv('WP_APP_PASSWORD')
    if not all([wp_url, wp_user, wp_app_password]):
        logging.error("Missing WordPress credentials or URL.")
        return None
    
    try:
        image_response = requests_retry_session().get(image_url, stream=True, timeout=20)
        image_response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Failed to download image: {e}")
        return None

    file_name = os.path.basename(image_url.split("?")[0])
    file_extension = file_name.split('.')[-1].lower()
    extension_to_mime = {
        'jpeg': 'image/jpeg',
        'jpg': 'image/jpeg',
        'png': 'image/png',
        'gif': 'image/gif',
        'svg': 'image/svg+xml'
    }
    content_type = image_response.headers.get('Content-Type', extension_to_mime.get(file_extension, 'application/octet-stream'))
    credentials = f'{wp_user}:{wp_app_password}'
    token = base64.b64encode(credentials.encode())
    headers = {
        'Authorization': f'Basic {token.decode("utf-8")}',
        'Content-Disposition': f'attachment; filename="{file_name}"',
        'Content-Type': content_type
    }

    try:
        response = requests_retry_session().post(
            url=f'{wp_url}/wp-json/wp/v2/media',
            headers=headers,
            data=image_response.content,
            timeout=20
        )
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Failed to upload image: {e}")
        return None

    image_id = response.json().get('id')
    if image_id:
        logging.info(f'Successfully uploaded image with ID: {image_id}')
        images_collection.insert_one({"url": image_url, "id": image_id})
        return image_id
    else:
        logging.error(f'Failed to upload image. Response: {response.content}')
        return None
    
def load_category(categories):
    category_ids = []
    for category in categories:
        response = wcapi.get("products/categories", params={"search": category}).json()
        if response:
            category_ids.append({"id": response[0]['id']})
        else:
            data = {"name": category}
            new_category_response = wcapi.post("products/categories", data).json()
            if 'id' in new_category_response:
                category_ids.append({"id": new_category_response['id']})
            else:
                logging.error(f"Failed to create category: {category}. Response: {new_category_response}")
    return category_ids

def create_attribute_if_not_exists(attribute_name):
    attribute_slug = attribute_name.lower().replace(' ', '_')
    attribute_type = "color" if "color" in attribute_name.lower() else "select"

    response = wcapi.get("products/attributes", params={"search": attribute_name}).json()
    for attr in response:
        if attr['name'].lower() == attribute_name.lower():
            return attr['id']

    data = {
        "name": attribute_name,
        "slug": attribute_slug,
        "type": attribute_type
    }

    response = wcapi.post("products/attributes", data).json()
    if 'id' in response:
        return response['id']
    else:
        logging.error(f"Failed to create attribute '{attribute_name}'. Response: {response}")
        return None

def create_variable_product_if_not_exists(product, attributes):
    name = product['name']
    response = wcapi.get("products", params={"search": name}).json()
    for existing_product in response:
        if existing_product['name'].lower() == name.lower() and existing_product['type'] == 'variable':
            return existing_product['id']

    image_id = upload_image_from_url_to_wordpress(product['images'][0]['src'])
    if not image_id:
        return None

    product_data = {
        "name": name,
        "type": "variable",
        "status": "publish",
        "stock_status": "instock",
        "categories": load_category(product["categories"]),
        "images": [{"id": image_id}],
        "attributes": [{
            "id": attribute['id'],
            "variation": True,
            "visible": True,
            "options": [Color(option, 'xkcd').name if 'color' in attribute["name"].lower() else option for option in attribute['options']]
        } for attribute in attributes]
    }
    response = wcapi.post("products", product_data).json()
    if 'id' in response:
        return response['id']
    else:
        logging.error(f"Failed to create variable product '{name}'. Response: {response}")
        return None

def create_variation(product_id, variation_data):
    if float(variation_data['regular_price']) == 0:
        return None

    existing_variations = wcapi.get(f"products/{product_id}/variations").json()
    for variation in existing_variations:
        if len(variation['attributes']) == len(variation_data['attributes']) and \
           all(variation['attributes'][i]['option'] == variation_data['attributes'][i]['option'] 
               for i in range(len(variation_data['attributes']))):
            return variation['id']

    variation_payload = {
        "regular_price": variation_data['regular_price'],
        "attributes": variation_data['attributes'],
        "meta_data": [variation_data.get('quantity_prices', [])]
    }

    if 'image' in variation_data:
        variation_payload['image'] = variation_data['image']

    response = wcapi.post(f"products/{product_id}/variations", variation_payload).json()
    if 'id' in response:
        return response['id']
    else:
        logging.error(f"Failed to create variation. Response: {response}")
        return None

def load_product(product):
    product = product['woo_data']

    existing_product = wcapi.get("products", params={"search": product['name']}).json()
    if product['type'] == 'simple':
        images = [{"id": upload_image_from_url_to_wordpress(x['src'])} for x in product.get('images', [])]
        data = {
            "name": product['name'],
            "type": "simple",
            "regular_price": str(product.get('regular_price', '0')),
            "description": product.get('description', ''),
            "categories": load_category(product["categories"]),
            "status": "publish",
            "stock_status": "instock",
            "images": images,
            "meta_data": [product.get("quantity_prices")]
        }

        if not all(data.values()) or float(data['regular_price']) == 0:
            data["status"] = "draft"

        if existing_product:
            wcapi.put(f"products/{existing_product[0]['id']}", data).json()
        else:
            wcapi.post("products", data).json()
    
    elif product['type'] == 'variable':
        attributes = [{"id": create_attribute_if_not_exists(attribute['name']), "name": attribute['name'], "options": attribute['options']} for attribute in product['attributes']]
        product_id = create_variable_product_if_not_exists(product, attributes)
        if not product_id:
            return

        variations = []
        for variant in product['variations']:
            variant['image'] = {"id": upload_image_from_url_to_wordpress(variant['image']["src"])}
            variant['regular_price'] = str(variant.get('regular_price', '0'))
            variations.append(variant)
        
        with ThreadPoolExecutor() as executor:
            future_variations = {executor.submit(create_variation, product_id, variation): variation for variation in variations}
            for future in as_completed(future_variations):
                future.result()

def fetch_all_data_from_mongodb():
    return list(collection.find({"status": "done"}).limit(100))

def load_to_woocommerce():
    all_products = fetch_all_data_from_mongodb()
    with tqdm(total=len(all_products), desc="Processing Products") as pbar:
        for product_data in all_products:
            load_product(product_data)
            pbar.update(1)

if __name__ == "__main__":
    load_to_woocommerce()
