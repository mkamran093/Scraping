import requests
import xml.etree.ElementTree as ET
import os
from pymongo import MongoClient, UpdateOne
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm  # For a nice progress bar

def fetch_urls_and_store_in_mongodb(sitemap_url):
    # Connect to MongoDB
    mongo_uri = os.getenv('MONGO_URI')
    mongo_db_name = os.getenv('MONGO_DB_NAME')
    mongo_collection_name = "products"

    assert mongo_uri is not None, "MONGO_URI is not set"
    assert mongo_db_name is not None, "MONGO_DB is not set"
    assert mongo_collection_name is not None, "MONGO_COLLECTION is not set"

    client = MongoClient(mongo_uri)
    db = client[mongo_db_name]
    collection = db[mongo_collection_name]

    # Create a unique index on the 'url' field if it doesn't already exist
    collection.create_index('url', unique=True)

    response = requests.get(sitemap_url)
    response.raise_for_status()
    root = ET.fromstring(response.content)
    ns = {'sitemap': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

    excluded_url = "https://www.vistaprint.com/holiday/christmas-cards"

    # List comprehension to filter out the excluded URL
    urls = [
        url_entry.find('sitemap:loc', namespaces=ns).text
        for url_entry in root.findall('.//sitemap:url', namespaces=ns)
        if url_entry.find('sitemap:loc', namespaces=ns).text != excluded_url
    ]

    total_urls = len(urls)

    print(f"Processing {total_urls} URLs from sitemap...")

    def process_url(loc):
        return UpdateOne({'url': loc}, {'$setOnInsert': {'url': loc, 'status': 'draft'}}, upsert=True)

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(process_url, url) for url in urls]
        updates = []
        for future in tqdm(futures, total=total_urls):
            updates.append(future.result())

            # Batch update every 1000 URLs
            if len(updates) >= 1000:
                collection.bulk_write(updates)
                updates.clear()

        # Final batch update
        if updates:
            collection.bulk_write(updates)

    print(f"Processed {total_urls} URLs")
    client.close()

# Test the code here
fetch_urls_and_store_in_mongodb('https://www.vistaprint.com/sitemaps/product.xml')
