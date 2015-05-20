# coding: utf-8
from os.path import exists

from urlparse import urljoin
from dateutil import parser
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.selector import Selector
from scrapy.utils.response import get_base_url

from comics.utils import remove_disallowed_filename_chars, download


class SATWSpider(CrawlSpider):
    PATH = 'Archive/SatW'
    name = 'satw'
    start_urls = ['http://satwcomic.com/the-world', ]
    allowed_domains = ['satwcomic.com', ]
    rules = (
        Rule(SgmlLinkExtractor(allow=(r'/page\d+', )), follow=True),
        Rule(SgmlLinkExtractor(
            allow=(r'.+',), restrict_xpaths=('//div[@class="thumbnail"]', )
        ), callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        sel = Selector(response)
        image_title = sel.xpath('//h1/text()').extract()[0]
        image_url = sel.xpath('//div[@class="container"]/center//img/@src').extract()[0]
        date = sel.xpath('//div[@class="row"]/div[@class="col-md-9"]/small/text()').extract()
        date = parser.parse([x for x in date if x.strip()][0]).strftime(u'%Y-%m-%d')
        base_url = get_base_url(response)
        image_url = urljoin(base_url, image_url)
        _, ext = image_url.split('/')[-1].split('.')
        image_name = u'{}.{}.{}'.format(date, image_title, ext)
        path = self.PATH + '/' + remove_disallowed_filename_chars(image_name)
        if not exists(path):
            return download(image_url, path)
