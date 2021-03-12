import scrapy
# from ..items import ProxyTest
from ..items import FullnovelItem
import re
"""
1.从分类页面获取所有分类的url
2.访问每个分类页，获得每个分类的详情页
3.从详情页中获取数据
"""


class FullHongxiuSpiderSpider(scrapy.Spider):
    name = 'full_hongxiu_spider'
    # allowed_domains = ['icanhazip.com']
    # start_urls = ['http://icanhazip.com/']
    allowed_domains = ['www.hongxiu.com']
    start_urls = ['https://www.hongxiu.com']
    base_url = 'https://www.hongxiu.com'
    # def parse(self, response):
    #     item = ProxyTest()
    #     item['ip'] = response.text.strip()
    #     yield item
    category_url_page = 'https://www.hongxiu.com/category'
    header = {
        # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36',
        'Referer': 'https://www.hongxiu.com/',
        'Host': 'www.hongxiu.com',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
    }

    meta_dict = {
        'category_name': '',
        'category_referer': ''
    }

    def parse(self, response):
        if response.status == 200:
            yield scrapy.Request(self.category_url_page, callback=self.parse_rank_url, headers=self.header)
        else:
            yield from super().start_requests()

    def parse_rank_url(self, response):
        """
        这里用于解析排行列表并进行查看
        :param response:
        :return:
        """
        dd_list = response.xpath('//li[@class="type act"]/div[@class="type-list"]/dl/dd')
        for dd in dd_list[0:1]:
            category_url = dd.xpath('./a/@href')[0].extract()
            category_name = dd.xpath('./a/i/text()').extract()
            if len(category_name) == 0:
                self.meta_dict['category_name'] = 'error'
            else:
                self.meta_dict['category_name'] = category_name[0]

            complete_url = self.base_url + category_url
            self.meta_dict['category_referer'] = complete_url
            self.header['Referer'] = self.meta_dict['category_referer']
            # print(complete_url)
            yield scrapy.Request(complete_url, callback=self.parse_book_page, headers=self.header, meta=self.meta_dict)

    def parse_book_page(self, response):
        li_lists = response.xpath('//div[@class="right-book-list"]/ul/li')
        self.header['Referer'] = response.meta['category_referer']
        # 爬虫自动请求，下载请求优先是随意的
        for li in li_lists:
            book_url = li.xpath('./div[@class="book-info"]/h3/a/@href')[0].extract()
            complete_book_info = self.base_url + book_url
            yield scrapy.Request(complete_book_info, callback=self.parse_target_info,meta=response.meta, headers=self.header)
        next_page = response.xpath('//ul[@class="lbf-pagination-item-list"]/li[last()]/a/@href')[0].extract()
        if not str(next_page).__contains__('javascript:;'):
            next_page_url = self.base_url + next_page
            self.header['Referer'] = self.meta_dict['category_referer']
            self.meta_dict['category_referer'] = next_page_url
            yield scrapy.Request(next_page_url, callback=self.parse_book_page, headers=self.header, meta=self.meta_dict)

    def parse_target_info(self, response):
        item = FullnovelItem()
        b_category = response.meta['category_name']
        subcribe = '0'
        b_name = response.xpath('//div[@class="book-info"]/h1/em/text()')[0].extract()
        item['b_name'] = b_name
        b_author = response.xpath('//div[@class="book-info"]/h1/a/text()')[0].extract()
        item['b_author'] = b_author
        tags_li = response.xpath('//div[@class="book-info"]/p[@class="tag-box"]/span[@class="tag"]/i')
        tags_list = []
        for tag in tags_li:
            if len(tag.xpath('./@class')) == 0:
                tags_list.append(tag.xpath('./text()')[0].extract())
        b_type = '&'.join(tags_list)
        item['b_type'] = b_type
        b_intro = re.compile("['\n''    ''<br>''\u3000''\r'].*?").sub('', ''.join(
            response.xpath('//div[@class="book-info"]/p[@class="intro"]/text()').extract()))
        item['b_intro'] = '"'+ b_intro+ '"'
        number_map = {
            '万': 10000,
            '千': 1000
        }
        # 收藏量单位
        # measure = response.xpath('//div[@class="book-info"]/p[@class="total"]/em[2]/text()').extract()[0]
        measure = re.compile("<!-- <span>.*?<em>(.*?)</em> -->").findall(response.text)[0]
        # print(measure)
        # 收藏数目
        # recommand = response.xpath('//div[@class="book-info"]/p[@class="total"]/span[2]/text()').extract()[0]
        # 点击量
        recommand = re.compile("<!-- <span>(.*?)</span>").findall(response.text)[0]
        # print(recommand)
        # print(measure[0])
        if len(measure) > 3:
            subcribe = str(float(recommand) * number_map[measure[0]])
        else:
            subcribe = recommand
        item['b_click'] = subcribe
        item['b_category'] = b_category
        print(response.request.headers)
        yield item