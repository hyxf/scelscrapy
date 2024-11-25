import scrapy


class SouGouItem(scrapy.Item):
    cate = scrapy.Field()
    title = scrapy.Field()
    href = scrapy.Field()
    sample = scrapy.Field()
    download_url = scrapy.Field()
    download_count = scrapy.Field()
    update_time = scrapy.Field()
