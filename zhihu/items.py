# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ZhihuItem(scrapy.Item):
    # all stats field
    is_followed = scrapy.Field()
    avatar_url_template = scrapy.Field()
    user_type = scrapy.Field()
    answer_count = scrapy.Field()
    is_following = scrapy.Field()
    url = scrapy.Field()
    url_token = scrapy.Field()
    id_ = scrapy.Field()
    articles_count = scrapy.Field()
    name = scrapy.Field()
    headline = scrapy.Field()
    type_ = scrapy.Field()
    is_advertiser = scrapy.Field()
    avatar_url = scrapy.Field()
    is_org = scrapy.Field()
    gender = scrapy.Field()
    follower_count = scrapy.Field()
    badge = scrapy.Field()
    crawl_time = scrapy.Field()