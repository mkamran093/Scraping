import os
from dotenv import load_dotenv
import scrapy
import json
from urllib.parse import urlencode, quote_plus
from common.database import MongoDB

load_dotenv()

class PricingSpider(scrapy.Spider):
    name = 'products_price'
    allowed_domains = ['vistaprint.com']

    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'CONCURRENT_REQUESTS': 32,  # Increase concurrency
        'DOWNLOAD_DELAY': 0,  # No delay between requests
        'RETRY_ENABLED': False,
        'REDIRECT_ENABLED': False,
        'HTTPCACHE_ENABLED': True,  # Enable HTTP cache
        'HTTPCACHE_EXPIRATION_SECS': 0,
        'HTTPCACHE_DIR': 'httpcache',
        'HTTPCACHE_IGNORE_HTTP_CODES': [500, 502, 503, 504, 408],
    }

    def __init__(self, *args, **kwargs):
        super(PricingSpider, self).__init__(*args, **kwargs)
        # Initialize the MongoDB connection using the shared MongoDB class
        self.mongo_db = MongoDB()
        self.db = self.mongo_db.get_collection('products')
        self.db.create_index('options')
        self.db.create_index('_id')

    def start_requests(self):
        products = self.db.find({
            'options': {'$exists': True},
        })

        for product in products:
            options = product.get('options', [])
            if options:
                for option in options:
                    selections = option.get('selections', {})
                    url = self.construct_url(product, selections)
                    meta = {
                        'product_id': product['_id'],
                        'option_index': product['options'].index(option)
                    }
                    yield scrapy.Request(url, callback=self.parse, meta=meta)
            else:
                url = self.construct_url(product, {})
                meta = {
                    'product_id': product['_id'],
                    'option_index': -1
                }
                yield scrapy.Request(url, callback=self.parse, meta=meta)

    def construct_url(self, product, selections):
        query_params = {
            'selections': json.dumps(selections),
            'productPageOptions': json.dumps(list(selections.keys())),
            'quantities': '[]',
            'version': product.get('mvp_version', ''),
            'applyProductConstraints': 'true',
            'mpvId': product.get('mvp_id', ''),
            'requestor': 'product-page-v2',
            'currentQuantity': 50,
            'optimizelyEndUserId': '_77678026-10d1-403e-87a9-624f3a1c65f0',
        }
        encoded_params = urlencode(query_params, quote_via=quote_plus)
        return f'https://product-pages-v2-bff.prod.merch.vpsvc.com/v1/compatibility-pricing/vistaprint/en-US/{product["mvp_id"]}?{encoded_params}'

    def parse(self, response):
        pricing_data = json.loads(response.text).get('pricing', {}).get('default', {})
        product_id = response.meta['product_id']
        option_index = response.meta['option_index']

        woo_data = self.db.find_one({'_id': product_id}, {'woo_data': 1}).get('woo_data', {})

        if option_index == -1:
            if 'variations' in woo_data:
                for variation in woo_data['variations']:
                    variation['regular_price'] = pricing_data.get('1', {}).get('unitListPrice', {}).get('untaxed', '0.00')
                    variation['quantity_prices'] = {
                        str(qty): price['unitListPrice']['untaxed'] for qty, price in pricing_data.items()
                    }
            else:
                woo_data['regular_price'] = pricing_data.get('1', {}).get('unitListPrice', {}).get('untaxed', '0.00')
                woo_data['quantity_prices'] = {str(qty): price['unitListPrice']['untaxed'] for qty, price in pricing_data.items()}
        else:
            if 'variations' in woo_data:
                woo_data['variations'][option_index]['regular_price'] = pricing_data.get('1', {}).get('unitListPrice', {}).get('untaxed', '0.00')
                woo_data['variations'][option_index]['quantity_prices'] = {
                    str(qty): price['unitListPrice']['untaxed'] for qty, price in pricing_data.items()
                }

        self.db.update_one({'_id': product_id}, {'$set': {'woo_data': woo_data, 'status': 'done'}})

    def close(self, reason):
        # Ensure to close MongoDB connection properly
        if self.mongo_db.client:
            self.mongo_db.client.close()
