# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
# from itemadapter import ItemAdapter
# import pymongo

class VpScraperPipeline:
    def process_item(self, item, spider):
        return item

# class MongoPipeline:
#     def open_spider(self, spider):
#         self.client = pymongo.MongoClient('mongodb://localhost:27017/')
#         self.db = self.client['product_database']

#     def close_spider(self, spider):
#         self.client.close()

#     def process_item(self, item, spider):
#         self.db['products'].insert_one(dict(item))
#         return item
