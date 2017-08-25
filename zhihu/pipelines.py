# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo
class ZhihuPipeline(object):
    collection_name = "zhihu_userdb"

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings.get("MONGO_URI"), crawler.settings.get("MONGO_DATABASE", "zhihu_userdb"))

    def open_spider(self, spider):
        self.client_connection = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client_connection[self.mongo_db]

    def close_spider(self, spider):
        self.client_connection.close()

    def process_item(self, item, spider):
        self.db[self.collection_name].insert_one(dict(item))
        return item
