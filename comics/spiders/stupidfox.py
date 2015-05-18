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
    PATH = 'Archive/StupidFox'
    name = 'fox'
    start_urls = ['http://stupidfox.net/archive', ]
    allowed_domains = ['stupidfox.net', ]
    rules = (
        Rule(SgmlLinkExtractor(allow=(r'/archive/page\d+',)), follow=True),
        Rule(SgmlLinkExtractor(
            allow=(r'.+',), restrict_xpaths=('//div[@class="thumb_box_smallthumb"]',)
        ), callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        sel = Selector(response)
        orig_name = sel.xpath('//h1/text()').extract()[0]
        date = parser.parse(sel.xpath('//div[@class="stand_high"]/small/text()').extract()[0]).strftime(u'%Y-%m-%d')
        image_url = sel.xpath('//div[@class="comicmid"]//img/@src').extract()[0]
        base_url = get_base_url(response)
        image_url = urljoin(base_url, image_url)
        _, ext = image_url.split('/')[-1].split('.')
        image_name = u'{}.{}.{}'.format(date, orig_name, ext)
        path = self.PATH + '/' + remove_disallowed_filename_chars(image_name)
        if not exists(path):
            return download(image_url, path)
