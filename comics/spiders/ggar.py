# coding: utf-8
from os.path import exists

from urlparse import urljoin
from dateutil import parser
from scrapy.contrib.spiders import CrawlSpider
from scrapy.http import Request
from scrapy.selector import Selector
from scrapy.utils.response import get_base_url

from comics.utils import remove_disallowed_filename_chars, download


class IAmArgSpider(CrawlSpider):
    PATH = 'Archive/GoGetARoomie'
    name = 'ggar'
    start_urls = ['http://www.gogetaroomie.com/comic/archive', ]
    allowed_domains = ['gogetaroomie.com', ]

    def parse_start_url(self, response):
        sel = Selector(response)
        comics = sel.xpath('//select/option')
        for c in comics:
            if c.xpath('./@value').extract()[0]:
                meta = {'date_text': c.xpath('./text()').extract()[0]}
                url = u'http://www.gogetaroomie.com/comic/' + c.xpath('./@value').extract()[0]
                yield Request(url, meta=meta, callback=self.parse_item)

    def parse_item(self, response):
        sel = Selector(response)
        image_url = sel.xpath('//div[@id="cc-comicbody"]//img/@src').extract()[0]
        date, image_name = response.meta.get('date_text').split(' - ')
        date = parser.parse(date).strftime(u'%Y-%m-%d')
        base_url = get_base_url(response)
        image_url = urljoin(base_url, image_url)
        _, ext = image_url.split('/')[-1].split('.')
        image_name = u'{}.{}.{}'.format(date, image_name, ext)
        path = self.PATH + '/' + remove_disallowed_filename_chars(image_name)
        if not exists(path):
            return download(image_url, path)
