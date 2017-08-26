# scrapyproj - usr data  on <https://www.zhihu.com>
Get user data on zhihu.com and write it to local MongoDB based on SCRAPY.

#### Dev Environment :
    * python 3.6.2
    * scrapy 1.3.3
    * pymongo 3.4.0
    
Fisrst get cookies after manually login to `zhihu.com` by chrome and press `F12` -> `Application` -> `Cookies` -> `write to spiders later`




Then get api from `zhihu.com` `F12` -> `Network(sort by type)` -> `read requests' headers which type is 'fetch'` -> `get query url`




e.g. https://www.zhihu.com/api/v4/members/{some_one}/followees?include=data%5B%2A%5D.answer_count%2Carticles_count%2Cgender%2Cfollower_count%2Cis_followed%2Cis_following%2Cbadge%5B%3F%28type%3Dbest_answerer%29%5D.topics&limit=20&offset=0




The core algorithm is crawl one user and his(her) followees, then crawl followees and his(her) followees.



if get banned (returns `<http 429>`, `<http 403>` response) :


1.Setting `DOWNLOAD_DELAY` from `setting.py` to roughly avoid getting banned

2.No proxy and user-agent plugin now, you can add it by yourself. (Refer to [offcial doc](https://doc.scrapy.org/en/latest/topics/practices.html#avoiding-getting-banned))
