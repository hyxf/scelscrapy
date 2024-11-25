import urllib.parse
from typing import Iterable

import scrapy
from scrapy import Request

from scelscrapy.items import SouGouItem


class SougouSpider(scrapy.Spider):
    name = "sougou"
    allowed_domains = ["pinyin.sogou.com"]

    def start_requests(self) -> Iterable[Request]:
        urls = [
            "https://pinyin.sogou.com/dict/cate/index/1",
            "https://pinyin.sogou.com/dict/cate/index/76",
            "https://pinyin.sogou.com/dict/cate/index/96",
            "https://pinyin.sogou.com/dict/cate/index/127",
            "https://pinyin.sogou.com/dict/cate/index/132",
            "https://pinyin.sogou.com/dict/cate/index/436",
            "https://pinyin.sogou.com/dict/cate/index/154",
            "https://pinyin.sogou.com/dict/cate/index/389",
            "https://pinyin.sogou.com/dict/cate/index/367",
            "https://pinyin.sogou.com/dict/cate/index/31",
            "https://pinyin.sogou.com/dict/cate/index/403",
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

        city_url = "https://pinyin.sogou.com/dict/cate/index/180"
        yield scrapy.Request(url=city_url, callback=self.city_parse)

        # beijing
        yield scrapy.Request(url="https://pinyin.sogou.com/dict/cate/index/180", callback=self.parse)

    def city_parse(self, response):
        citys = response.css("#city_list_show > table > tbody > tr > td > div > a::attr(href)").getall()
        for city_href in citys:
            next_page = f"https://pinyin.sogou.com{city_href}"
            yield response.follow(next_page, callback=self.parse)

    def parse(self, response):
        cate = response.css(".cate_title::text").re("“(.*?)”")[0]
        details = response.css(".dict_detail_block")
        for detail in details:
            item = SouGouItem()

            item["cate"] = cate

            title = detail.css(".detail_title a::text").get()
            item["title"] = title

            href = detail.css(".detail_title a::attr(href)").get()
            item["href"] = f"https://pinyin.sogou.com{href}"

            show_content = detail.css(".dict_detail_content .show_content::text").getall()

            size = len(show_content)
            if size == 3:
                item["sample"] = show_content[0]
                item["download_count"] = show_content[1]
                item["update_time"] = show_content[2]
            elif size == 2:
                item["download_count"] = show_content[0]
                item["update_time"] = show_content[1]
            else:
                pass

            download_url = detail.css(".dict_dl_btn a::attr(href)").get()
            item["download_url"] = urllib.parse.unquote(download_url)

            yield item

        links = response.css("#dict_page_list > ul > li > span")
        for link in links:
            link_text = link.css("a::text").get()
            link_href = link.css("a::attr(href)").get()
            if "下一页" == link_text:
                next_page = f"https://pinyin.sogou.com{link_href}"
                yield response.follow(next_page, callback=self.parse)
