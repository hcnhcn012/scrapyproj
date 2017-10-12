# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html



# Pipeline's ORM functions partly referring to scrapy-mongodb
# from https://github.com/sebdah/scrapy-mongodb/blob/master/scrapy_mongodb.py


import logging
import datetime
from pymongo import errors
from pymongo.mongo_client import MongoClient
from pymongo.mongo_replica_set_client import MongoReplicaSetClient
from pymongo.read_preferences import ReadPreference
from scrapy.exporters import BaseItemExporter

class ZhihuPipeline(object):

    config = {
        'uri': 'mongodb://localhost:27017',
        'fsync': False,
        'write_concern': 1,
        'database': 'zhihu_userdb',
        'collection': 'zhihu_userdb',
        'separate_collections': False,
        'replica_set': None,
        'unique_key': None,
        'buffer': None,
        'append_timestamp': False,
        'stop_on_duplicate': 0,
    }

    current_item = 0

    item_buffer = []
    duplicate_key_count = 0


    def __init__(self, mongo_uri, mongo_db, mongo_replSet_name, mongo_replSet_uri):
        self.config["uri"] = mongo_uri
        self.config["database"] = mongo_db
        if mongo_replSet_name:
            #self.mongo_replSet_name = mongo_replSet_name
            self.config["replica_set"] = mongo_replSet_name
        if mongo_replSet_uri:
            #self.mongo_replSet_uri = mongo_replSet_uri
            self.config["uri"] = mongo_replSet_uri
        self.logger = logging.getLogger("scrapy-Zhihu-logger")
    @classmethod
    def from_crawler(cls, crawler):
        return cls(
                crawler.settings.get("MONGO_URI", "mongodb://localhost:27017/zhihu_userdb"),
                crawler.settings.get("MONGO_DATABASE", "zhihu_userdb"),
                crawler.settings.get("MONGO_REPLSET_NAME", "None"),
                crawler.settings.get("MONGO_REPLSET_URI", "None")
                )

    def open_spider(self, spider):
        self.crawler = spider.crawler
        self.settings = spider.settings
        if self.config["replica_set"] is not None:
            self.conncetion = MongoReplicaSetClient(
                self.config["uri"],
                replicaSet = self.config["replica_set"],
                w = self.config["write_concern"],
                fsync = self.config["fsync"],
                read_preferences = ReadPreference.PRIMARY_PREFERRED
            )

        else:
            self.connection = MongoClient(
                self.config["uri"],
                fsync = self.config["fsync"],
                read_preferences = ReadPreference.PRIMARY
            )
        self.database = self.conncetion[self.config["database"]]
        self.collections = {'default': self.database[self.config['collection']]}
        self.logger.info('Connected dbpath: {0}, database: {1}'.format(
            self.config["uri"],
            self.config["database"]
        ))
        if self.config['stop_on_duplicate']:
            tmpValue = self.config['stop_on_duplicate']

            if tmpValue < 0:
                msg = (
                    u'Negative values are not allowed for'
                    u' MONGODB_STOP_ON_DUPLICATE option.'
                )

                self.logger.error(msg)
                raise SyntaxError(msg)

            self.stop_on_duplicate = self.config['stop_on_duplicate']

        else:
            self.stop_on_duplicate = 0

    def close_spider(self, spider):
        if self.item_buffer:
            self.insert_item(self.item_buffer, spider)
        self.connection.close()

    def process_item(self, item, spider):
        item = dict((k, v) for k, v in item.iteritems() if v is not None and v != "")
        if self.config['buffer']:
            self.current_item += 1

            if self.config['append_timestamp']:
                item['scrapy-mongodb'] = {'ts': datetime.datetime.utcnow()}

            self.item_buffer.append(item)

            if self.current_item == self.config['buffer']:
                self.current_item = 0

                try:
                    return self.insert_item(self.item_buffer, spider)
                finally:
                    self.item_buffer = []

            return item

        return self.insert_item(item, spider)

    def insert_item(self, item, spider):
        if not isinstance(item, list):
            item = dict(item)

            if self.config['append_timestamp']:
                item['scrapy-mongodb'] = {'ts': datetime.datetime.utcnow()}

        collection_name, collection = self.get_collection(spider.name)

        if self.config['unique_key'] is None:
            try:
                collection.insert(item, continue_on_error=True)
                self.logger.debug(u'Stored item(s) in MongoDB {0}/{1}'.format(
                    self.config['database'], collection_name))

            except errors.DuplicateKeyError:
                self.logger.debug(u'Duplicate key found')
                if (self.stop_on_duplicate > 0):
                    self.duplicate_key_count += 1
                    if (self.duplicate_key_count >= self.stop_on_duplicate):
                        self.crawler.engine.close_spider(
                            spider,
                            'Number of duplicate key insertion exceeded'
                        )

        else:
            key = {}

            if isinstance(self.config['unique_key'], list):
                for k in dict(self.config['unique_key']).keys():
                    key[k] = item[k]
            else:
                key[self.config['unique_key']] = item[self.config['unique_key']]

            collection.update(key, item, upsert=True)

            self.logger.debug(u'Stored item(s) in MongoDB {0}/{1}'.format(
                self.config['database'], collection_name))
        return item

    def get_collection(self, name):
        if self.config['separate_collections']:
            collection = self.collections.get(name)
            collection_name = name

            if not collection:
                collection = self.database[name]
                self.collections[name] = collection
        else:
            collection = self.collections.get('default')
            collection_name = self.config['collection']
        if self.config['unique_key']:
            collection.ensure_index(self.config['unique_key'], unique=True)
            self.logger.info(u'Ensuring index for key {0}'.format(
                self.config['unique_key']))
        return (collection_name, collection)