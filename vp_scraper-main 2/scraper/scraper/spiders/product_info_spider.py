import os
from dotenv import load_dotenv
import scrapy
import json
from common.database import MongoDB
from scripts.fetch_sitemap import fetch_urls_and_store_in_mongodb
from scripts.fetch_product_info import fetch_and_update_product_documents

load_dotenv()

class ProductInfoSpider(scrapy.Spider):
    name = 'products_info'
    allowed_domains = ['vistaprint.com']

    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    }

    def __init__(self, *args, **kwargs):
        super(ProductInfoSpider, self).__init__(*args, **kwargs)
        self.mongo_db = MongoDB()
        self.prepare_scraping()
        self.collection = self.mongo_db.get_collection('products')

    def prepare_scraping(self):
        sitemap_url = os.getenv('SITEMAP_URL')
        if not sitemap_url:
            raise EnvironmentError('SITEMAP_URL environment variable is not set.')
        
        fetch_urls_and_store_in_mongodb(sitemap_url)
        fetch_and_update_product_documents()

    def start_requests(self):
        products = self.collection.find({"data_url": {"$exists": True}})
        for product in products:
            headers = {'Referer': product['url']}
            yield scrapy.Request(url=product['data_url'], callback=self.parse, headers=headers, meta={'product_id': product['_id']})

    def parse(self, response):
        data = json.loads(response.body)
        product_info = {
            'name': data['result']['pageContext']['item']['mpv']['name'],
            'description': data['result']['pageContext']['item']['description'],
            'image': data['result']['pageContext']['item'].get('heroGallery', [{}])[0].get('cloudinaryImage', {}).get('cloudinaryUrl'),
            'options': data['result']['pageContext']['item'].get('referentialImages', {}).get('referentialImages', []),
            'breadcrumbs': data['result']['pageContext']['breadcrumbs'],  # Get breadcrumbs for category
            'mvp_id': data['result']['pageContext']['item']['mpv']['coreProductId'],
            'mvp_version': data['result']['pageContext']['item']['mpv']['version']
        }
        file_path = 'product_info.json'
    
        # Write the product_info to the JSON file
        with open(file_path, 'w') as json_file:
            json.dump(product_info, json_file, indent=4)

        woo_data = self.map_to_woo_data(product_info)
        
        self.collection.update_one({'_id': response.meta['product_id']}, {'$set': {**product_info, 'woo_data': woo_data, 'status': 'processed'}})

    def map_to_woo_data(self, product_info):
        # Handle breadcrumbs to get categories
        breadcrumbs = product_info.get('breadcrumbs', [])
        categories = [bc['name'] for bc in breadcrumbs[-3:-1]]  # Get last three excluding the last one
        
        if not product_info['options']:
            woo_data = {
                'name': product_info['name'],
                'type': 'simple',
                'description': product_info['description'],
                'images': [{'src': product_info['image'], 'alt': product_info['name']}],
                'categories': categories,  # Add categories
                'regular_price': '0.00'  # Default price, update as needed
            }
        else:
            variations = []
            attributes = {}
            
            for option in product_info['options']:
                for key, value in option['selections'].items():
                    if key not in attributes:
                        attributes[key] = []
                    if value not in attributes[key]:
                        attributes[key].append(value)

            for option in product_info['options']:
                image = None
                if 'image' in option and 'cloudinaryImage' in option['image']:
                    image = {'src': option['image']['cloudinaryImage']['cloudinaryUrl'], 'alt': product_info['name']}

                variation = {
                    'attributes': [{'name': k, 'option': v} for k, v in option['selections'].items()],
                    'image': image,
                    'regular_price': '0.00'  # Default price, update as needed
                }
                variations.append(variation)

            woo_data = {
                'name': product_info['name'],
                'type': 'variable',
                'description': product_info['description'],
                'images': [{'src': product_info['image'], 'alt': product_info['name']}],
                'categories': categories,  # Add categories
                'attributes': [{'name': k, 'visible': True, 'variation': True, 'options': v} for k, v in attributes.items()],
                'variations': variations
            }
        return woo_data
