# coding: utf-8
from os.path import exists

from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.selector import Selector

from comics.utils import remove_disallowed_filename_chars, download


class YAFGCSpider(CrawlSpider):
    PATH = 'Archive/YAFGC'
    name = 'yafgc'
    start_urls = ['http://yafgc.net/archive/', ]
    allowed_domains = ['yafgc.net', ]
    rules = (
        Rule(SgmlLinkExtractor(allow=(r'/comic/.+/$',)), callback='parse_item'),
    )

    def parse_item(self, response):
        sel = Selector(response)
        image_data = sel.xpath('//div[@id="comic"]//img')
        image_url = image_data.xpath('./@src').extract()[0]
        full_title = sel.xpath('//h2[@class="post-title"]/text()').extract()[0]
        no, image_title = full_title.split(' ', 1)
        no = no.replace(':', '')
        if image_title[-1] == '.' and not image_title[-2] == '.':
            image_title = image_title[:-1]
        name, ext = image_url.split('/')[-1].rsplit('.', 1)
        image_name = u'{}.{}.{}'.format(int(no), image_title.strip(), ext)
        path = self.PATH + '/' + remove_disallowed_filename_chars(image_name)
        if not exists(path):
            return download(image_url, path)
