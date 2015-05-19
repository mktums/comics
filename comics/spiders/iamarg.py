# coding: utf-8
from os.path import exists

from urlparse import urljoin
from dateutil import parser
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.selector import Selector
from scrapy.utils.response import get_base_url

from comics.utils import remove_disallowed_filename_chars, download


class StupidFoxSpider(CrawlSpider):
    PATH = 'Archive/IAmArg'
    name = 'arg'
    start_urls = ['http://iamarg.com', ]
    allowed_domains = ['iamarg.com', ]
    rules = (
        Rule(SgmlLinkExtractor(
            allow=(r'/\d{4}/\d{2}/\d{2}/.+/$',),
            deny=(r'/feed/$',),
        ), callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        sel = Selector(response)
        try:
            image_url = sel.xpath('//div[@id="comic"]//img/@src').extract()[0]
        except:
            return
        post_info = sel.xpath('//div[@class="post-text"]')
        orig_name = post_info.xpath('./h2/a/text()').extract()[0]
        date = parser.parse(
            post_info.xpath('./span[@class="post-date"]/text()').extract()[0]
        ).strftime(u'%Y-%m-%d')
        base_url = get_base_url(response)
        image_url = urljoin(base_url, image_url)
        _, ext = image_url.split('/')[-1].split('.')
        image_name = u'{}.{}.{}'.format(date, orig_name, ext)
        path = self.PATH + '/' + remove_disallowed_filename_chars(image_name)
        if not exists(path):
            return download(image_url, path)
