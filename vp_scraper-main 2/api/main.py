from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import shlex
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.base import JobLookupError
from pydantic import BaseModel
from pymongo import MongoClient
from typing import List, Optional
from dotenv import load_dotenv
import os
from .service import load_to_woocommerce

# Load environment variables from .env file
load_dotenv()

# Get MongoDB connection details from environment variables
MONGO_URI = os.getenv('MONGO_URI')
MONGO_DB = os.getenv('MONGO_DB_NAME')

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
products_collection = db['products']

# Initialize FastAPI app
app = FastAPI()

# Configure CORS
origins = [
    "*",     # Replace with actual domain if needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            # Allows access only from specified origins
    allow_credentials=True,
    allow_methods=["*"],              # Allows all HTTP methods
    allow_headers=["*"],              # Allows all headers
)

# Initialize APScheduler
scheduler = BackgroundScheduler()
scheduler.start()

# Define a model for the input configuration data
class ScheduleConfig(BaseModel):
    scrape_all_interval_seconds: Optional[int] = None  # Interval for full scraping
    scrape_price_interval_seconds: Optional[int] = None  # Interval for price scraping only

# Function to run spider
def run_spider(spider_name: str):
    command = f"scrapy crawl {spider_name}"
    process = subprocess.Popen(shlex.split(command), cwd="scraper/")
    process.wait()

# Scheduled jobs that can be dynamically updated
def scheduled_full_scraping():
    run_spider('products_info')
    run_spider('products_price')

def scheduled_price_scraping():
    run_spider('products_price')

@app.post("/configure-scheduler/")
def configure_scheduler(config: ScheduleConfig):
    if config.scrape_all_interval_seconds is not None:
        try:
            scheduler.remove_job('full_scraping')
        except JobLookupError:
            pass
        scheduler.add_job(scheduled_full_scraping, 'interval', seconds=config.scrape_all_interval_seconds, id='full_scraping')
    
    if config.scrape_price_interval_seconds is not None:
        try:
            scheduler.remove_job('price_scraping')
        except JobLookupError:
            pass
        scheduler.add_job(scheduled_price_scraping, 'interval', seconds=config.scrape_price_interval_seconds, id='price_scraping')
    
    return {"message": "Scheduler updated according to configuration"}

@app.post("/trigger_scraping/")
def trigger_scraping():
    # Run both spiders one after another, waiting for each to complete
    run_spider('products_info')
    run_spider('products_price')
    return {"message": "Scraping process completed. All scripts have executed."}

@app.post("/trigger_price_scraping/")
def trigger_price_scraping():
    # Run the price scraping spider and wait for it to complete
    run_spider('products_price')
    return {"message": "Price scraping completed."}

@app.get("/products/", response_model=List[dict])
def get_all_products():
    products = list(products_collection.find({}, {"_id": 0}))  # Exclude the MongoDB object IDs
    if not products:
        raise HTTPException(status_code=404, detail="No products found")
    return products

@app.get("/product-count/")
def get_product_count():
    count = products_collection.count_documents({})
    return {"total_products": count}

@app.get("/failed-product-count/")
def get_failed_product_count():
    failed_count = products_collection.count_documents({"failed": True})
    return {"failed_products": failed_count}

@app.get("/load-to-woocommerce/")
def load_to_products_to_woocommerce():
    try:
        load_to_woocommerce()
        return {"message": "Data loaded to WooCommerce successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
