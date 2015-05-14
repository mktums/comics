# coding: utf-8
from dateutil import parser
from os.path import exists
from urlparse import urljoin
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.selector import Selector
from scrapy.utils.response import get_base_url
from comics.utils import remove_disallowed_filename_chars, download


class CMSpider(CrawlSpider):
    PATH = 'Archive/CriticalMiss'
    name = 'cm'
    start_urls = ['http://www.escapistmagazine.com/articles/view/comics/critical-miss', ]
    allowed_domains = ['escapistmagazine.com', ]
    rules = (
        Rule(SgmlLinkExtractor(allow=(r'articles/view/comics/critical-miss\.\d+$',)), follow=True),
        Rule(SgmlLinkExtractor(
            allow=(r'articles/view/comicsandcosplay/comics/critical-miss/.+$',),
            deny=(r'\.next$', r'\.prev$'),
        ), callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        sel = Selector(response)
        base_url = get_base_url(response)
        timestamp = sel.xpath('//meta[@itemprop="datePublished"]/@content').extract()[0]
        date = parser.parse(timestamp).strftime(u'%Y.%m.%d')
        try:
            image_title = sel.xpath('//h1/div[@class="name"]/text()').extract()[0].strip()
        except IndexError:
            try:
                image_title = sel.xpath('//h1/text()').extract()[0].replace(':', '').strip()
            except IndexError:
                everything = sel.xpath('//h1/*[not(self::a)]')
                image_title = u''.join([x.xpath('string(.)').extract()[0] for x in everything]).strip()

        try:
            image_url = sel.xpath('(//*[@itemprop="articleBody"]//img)[2]/@src').extract()[0]
        except IndexError:
            image_url = sel.xpath('//*[@itemprop="articleBody"]//img/@src').extract()[0]

        image_url = urljoin(base_url, image_url)
        _, ext = image_url.split('/')[-1].rsplit('.', 1)
        image_name = u'{}.{}.{}'.format(date, image_title, ext)
        path = self.PATH + '/' + remove_disallowed_filename_chars(image_name)
        if not exists(path):
            return download(image_url, path)
