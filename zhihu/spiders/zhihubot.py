import scrapy
import json
from datetime import datetime
from zhihu.items import ZhihuItem
from scrapy.loader import ItemLoader

# url model to crawl
url_to_crawl = "https://www.zhihu.com/api/v4/members/{}/followees?include=data%5B%2A%5D.answer_count%2Carticles_count%2Cgender%2Cfollower_count%2Cis_followed%2Cis_following%2Cbadge%5B%3F%28type%3Dbest_answerer%29%5D.topics&limit=20&offset=0"

class Zhihubot(scrapy.Spider):
    name = "zhihu"
    allowed_domains = ["www.zhihu.com"]
    # headers copy from chrome dev-toll except cookies
    # To skip robot auth :
    # First log on to the site and copy headers and cookies through chrome dev-tool
    # Or use another project fuck-login based on pillow : https://github.com/xchaoinfo/fuck-login

    #get your own headers
    headers = {
        "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding":"gzip, deflate, br",
        "Accept-Language":"en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4",
        "Cache-Control":"max-age=0",
        "Connection":"keep-alive",
        "Host":"www.zhihu.com",
        "Upgrade-Insecure-Requests":"1",
        "User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36"
    }
    # get your own cookies
    # get all cookies after manually log on to www.zhihu.com
    cookies = {
        "__utma" : "51854390.1686482292.1503669701.1503669701.1503669701.1",
        "__utmb" : "51854390.0.10.1503669701",
        "__utmc" : "51854390",
        "__utmv" : "51854390.000--|3=entry_date=20170825=1",
        "__utmz" : "51854390.1503669701.1.1.utmcsr=zhihu.com|utmccn=(referral)|utmcmd=referral|utmcct=/people/twinklymovie88/activities",
        "_xsrf" : "9b21001ed4b607d92f9013dbc4e415da",
        "_xsrf" : "9b21001ed4b607d92f9013dbc4e415da",
        "_zap" : "d7cc8c16-9ccf-4c89-a26d-b8cc1993b283",
        "aliyungf_tc" : "AQAAAG4u8BFBQAUABYB6fVdVVrIG3+01",
        "cap_id" : '"NmFlYmZlMzAyODM2NGFmZGFkMzczMmM0NzlkYjcxMzc=|1503669700|ece821c77201a22a1a4ea3c63a5bebbee3a3495e"',
        "d_c0" : '"AICCeV2ARgyPTgvRirfnBhB8qBuawdKGSb0=|1503669700"',
        "l_n_c" : "1",
        "q_c1" : "5df7e924c2bd44508fc876a905ab14f5|1503669700000|1503669700000",
        "r_cap_id" : '"MWM4YTk1N2Y3ZTRiNDc2Mjk4NzY2MDk1Yzc2NjVjYzk=|1503669700|23091cb6abb1e8d8654c4d5111bd459ecdb1c524"',
        "z_c0" : "Mi4xeFR4ZkFnQUFBQUFBZ0lKNVhZQkdEQmNBQUFCaEFsVk4wN3JIV1FDXzZkWF9FaV84WFJKVWp6SzIxbWh4a2F3dEdB|1503669715|ad8a8160da6a785d7546bed0be78cea85a76acd2"
    }

    def start_requests(self):
        yield scrapy.http.Request(url_to_crawl.format("he-ming-ke"), callback=self.parse, headers=self.headers, cookies=self.cookies)
    def parse(self, response):
        #see the page testing if logged in using cookies
        #with open("zhihu.com", "wb") as f:
            #f.write(response.body)
        
        #deserialize the json response
        response_json = json.loads(response.text)

        if not response_json["paging"]["is_end"]:
            yield scrapy.http.Request(response_json["paging"]["next"], callback=self.parse, headers=self.headers, cookies=self.cookies)
        if response_json["data"]:
            for data in response_json["data"]:
                if data["url_token"]:
                    yield scrapy.http.Request(url_to_crawl.format(data["url_token"]), callback=self.parse, headers=self.headers, cookies=self.cookies)
                    zhihu_itemloader = ItemLoader(item=ZhihuItem(), response=response)
                    zhihu_itemloader.add_value("is_followed", data["is_followed"])
                    zhihu_itemloader.add_value("avatar_url_template", data["avatar_url_template"])
                    zhihu_itemloader.add_value("user_type", data["user_type"])
                    zhihu_itemloader.add_value("answer_count", data["answer_count"])
                    zhihu_itemloader.add_value("is_following", data["is_following"])
                    zhihu_itemloader.add_value("url", data["url"])
                    zhihu_itemloader.add_value("url_token", data["url_token"])
                    zhihu_itemloader.add_value("id_", data["id"])
                    zhihu_itemloader.add_value("articles_count", data["articles_count"])
                    zhihu_itemloader.add_value("name", data["name"])
                    zhihu_itemloader.add_value("headline", data["headline"])
                    zhihu_itemloader.add_value("type_", data["type"])
                    zhihu_itemloader.add_value("is_advertiser", data["is_advertiser"])
                    zhihu_itemloader.add_value("avatar_url", data["avatar_url"])
                    zhihu_itemloader.add_value("is_org", data["is_org"])
                    zhihu_itemloader.add_value("gender", data["gender"])
                    zhihu_itemloader.add_value("follower_count", data["follower_count"])
                    zhihu_itemloader.add_value("badge", data["badge"])
                    zhihu_itemloader.add_value("crawl_time",datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    yield zhihu_itemloader.load_item()