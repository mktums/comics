# coding: utf-8
from os.path import exists
from urlparse import urljoin
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.selector import Selector
from scrapy.utils.response import get_base_url
from comics.utils import download


class LFGSpider(CrawlSpider):
    PATH = 'Archive/Vitaliy'
    name = 'vit'
    start_urls = ['http://schakty.com/tagvitaliy/', ]
    allowed_domains = ['schakty.com', ]
    rules = (
        Rule(SgmlLinkExtractor(
            allow=(r'/\d{4}/.+/$',), restrict_xpaths='//div[@id="main-content"]'
        ), follow=False, callback='parse_item'),
    )

    def parse_item(self, response):
        sel = Selector(response)
        base_url = get_base_url(response)
        image_title = sel.xpath('//h1/text()').extract()[0]
        image_urls = sel.xpath('//div[@class="entry-content"]//img/@src').extract()
        for idx, _image_url in enumerate(image_urls):
            image_url = urljoin(base_url, _image_url)
            _, ext = image_url.split('/')[-1].rsplit('.', 1)
            if len(image_urls) > 1:
                image_name = u'{}-{}.{}'.format(image_title, idx+1, ext)
            else:
                image_name = u'{}.{}'.format(image_title, ext)
            path = self.PATH + '/' + image_name
            if not exists(path):
                return download(image_url, path)
