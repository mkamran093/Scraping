import os
import time
import logging
from pymongo import MongoClient, UpdateOne
from playwright.sync_api import sync_playwright
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
from tqdm import tqdm  # Import tqdm for progress tracking

# Configure logging
logging.basicConfig(
    filename='scraper_errors.log',
    level=logging.ERROR,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def fetch_product_data(document):
    found_url = None
    retry_count = 0

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()

        while retry_count < 5:
            page = context.new_page()

            def handle_request(request):
                nonlocal found_url
                url = request.url
                if "page-data" in url and url.endswith('.json') and "app-data.json" not in url:
                    found_url = url

            page.on('request', handle_request)

            try:
                page.goto(document['url'], wait_until='domcontentloaded', timeout=10000)
                page.wait_for_timeout(3000)
                if found_url:
                    break
                page.reload()
                page.wait_for_timeout(3000)
                if found_url:
                    break
            except Exception as e:
                logger.error(f"Error loading page {document['url']}: {e}")
            finally:
                page.remove_listener('request', handle_request)
                page.close()

            retry_count += 1
            if retry_count < 5:
                time.sleep(5)  # Wait for 5 seconds before retrying

        browser.close()

    if not found_url:
        logger.warning(f"Failed to find URL for document {document['_id']} after 5 attempts.")

    return document['_id'], found_url

def fetch_and_update_product_documents():
    load_dotenv()
    mongo_uri = os.getenv('MONGO_URI')
    mongo_db_name = os.getenv('MONGO_DB_NAME')
    mongo_collection_name = "products"

    assert mongo_uri is not None, "MONGO_URI is not set"
    assert mongo_db_name is not None, "MONGO_DB is not set"
    assert mongo_collection_name is not None, "MONGO_COLLECTION is not set"

    client = MongoClient(mongo_uri)
    db = client[mongo_db_name]
    collection = db[mongo_collection_name]

    documents_to_process = list(collection.find({}))
    total_documents = len(documents_to_process)

    logger.info(f"Processing {total_documents} documents...")

    def process_document(document):
        try:
            return fetch_product_data(document)
        except Exception as e:
            logger.error(f"Error processing document {document['_id']}: {e}")
            return document['_id'], None

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(process_document, doc) for doc in documents_to_process]
        updates = []
        processed_count = 0

        # Use tqdm to display a progress bar
        for future in tqdm(as_completed(futures), total=total_documents, desc="Processing documents"):
            try:
                doc_id, found_url = future.result()
                if found_url:
                    updates.append(UpdateOne(
                        {"_id": doc_id},
                        {"$set": {"data_url": found_url}}
                    ))
                processed_count += 1
                if processed_count % 100 == 0:
                    logger.info(f"Processed {processed_count} of {total_documents} documents")

                # Batch update every 100 documents
                if len(updates) >= 10:
                    collection.bulk_write(updates)
                    updates.clear()
            except Exception as e:
                logger.error(f"Error handling future result: {e}")

        # Final batch update
        if updates:
            collection.bulk_write(updates)

    logger.info(f"Completed processing {total_documents} documents")
    client.close()

if __name__ == '__main__':
    fetch_and_update_product_documents()
