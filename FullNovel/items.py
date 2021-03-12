# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class FullnovelItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # rank_url = scrapy.Field()
    b_author = scrapy.Field()
    b_name = scrapy.Field()
    b_type = scrapy.Field()
    b_intro = scrapy.Field()
    b_click = scrapy.Field()
    b_category = scrapy.Field()

class ProxyTest(scrapy.Item):
    ip = scrapy.Field()
