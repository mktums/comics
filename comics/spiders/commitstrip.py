# coding: utf-8
import re
from os.path import exists
from urlparse import urlparse

from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.selector import Selector

from comics.utils import download, remove_disallowed_filename_chars


class CSSpider(CrawlSpider):
    PATH = 'Archive/CommitStrip'
    name = 'commitstrip'
    start_urls = ['http://www.commitstrip.com/en/', ]
    allowed_domains = ['www.commitstrip.com', ]
    rules = (
        Rule(SgmlLinkExtractor(
            allow=(r'/en/\d{4}/\d{2}/\d{2}/.+/$',)
        ), callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        sel = Selector(response)
        img_data = sel.xpath('//div[@id="content"]//article/div[@class="entry-content"]//img')
        image_url = img_data.xpath('./@src').extract()[0]
        if not urlparse(image_url).scheme:
            image_url = urlparse(image_url)._replace(scheme=urlparse(response.url).scheme).geturl()

        image_title = sel.xpath('//h1[@class="entry-title"]/text()').extract()[0]
        _, ext = image_url.split('/')[-1].rsplit('.', 1)
        date = '-'.join(re.search(r'/en/(\d{4})/(\d{2})/(\d{2})/', response.url).groups())
        image_name = u'{}.{}.{}'.format(date, image_title, ext)
        path = self.PATH + '/' + remove_disallowed_filename_chars(image_name)
        if not exists(path):
            return download(image_url, path)
