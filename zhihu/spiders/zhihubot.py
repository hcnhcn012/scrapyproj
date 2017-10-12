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
        # add your cookies by press F12 -> Application -> Cookies on Chrome
    }

    def start_requests(self):
        yield scrapy.http.Request(url_to_crawl.format("some-one"), callback=self.parse, headers=self.headers, cookies=self.cookies)
    def parse(self, response):
        #see the page testing if loggedin by using cookies above
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