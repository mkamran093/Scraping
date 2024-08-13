import os
from dotenv import load_dotenv
import logging
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

load_dotenv()

class MongoDB:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoDB, cls).__new__(cls)
            cls._instance.client = None
            cls._instance.db = None
        return cls._instance

    def connect(self):
        """ Connect to MongoDB database. """
        if not self.client:
            try:
                mongo_uri = os.getenv('MONGO_URI')
                if not mongo_uri:
                    raise EnvironmentError('MONGO_URI environment variable not set.')
                
                self.client = MongoClient(mongo_uri)
                db_name = os.getenv('MONGO_DB_NAME')
                if not db_name:
                    raise EnvironmentError('MONGO_DB_NAME environment variable not set.')
                self.db = self.client[db_name]
                self.client.admin.command('ping')
            except (ConnectionFailure, EnvironmentError) as e:
                logging.error(f"MongoDB connection failed: {e}")
                raise

    def get_collection(self, collection_name):
        """ Retrieve a collection from the connected database. """
        if self.db is None:
            self.connect()
        return self.db[collection_name]

# Usage example:
# mongo_db = MongoDB()
# product_collection = mongo_db.get_collection('product_urls')
