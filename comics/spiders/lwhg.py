# coding: utf-8
from os.path import exists

from urlparse import urljoin
from scrapy.contrib.spiders import CrawlSpider
from scrapy.http import Request
from scrapy.selector import Selector
from scrapy.utils.response import get_base_url

from comics.utils import remove_disallowed_filename_chars, download


class LWHGSpider(CrawlSpider):
    PATH = 'Archive/LWHG'
    name = 'lwhg'
    start_urls = ['http://www.jagodibuja.com/webcomic-living-with-hipstergirl-and-gamergirl-english/', ]
    allowed_domains = ['jagodibuja.com', ]

    def parse_start_url(self, response):
        sel = Selector(response)
        image_url = sel.xpath('//div[@class="entry-content"]/p/a/@href').extract()[0]
        base_url = get_base_url(response)
        image_url = urljoin(base_url, image_url)
        _, ext = image_url.split('/')[-1].split('.')
        image_name = u'_characters.{}'.format(ext)
        path = self.PATH + '/' + remove_disallowed_filename_chars(image_name)
        if not exists(path):
            download(image_url, path)

        images = sel.xpath('//figure[@class="gallery-item"]//a/@href').extract()
        for i, c in enumerate(images):
            yield Request(c, meta={'index': i+1}, callback=self.parse_item)

    def parse_item(self, response):
        sel = Selector(response)
        image_url = sel.xpath('//span[@class="full-size-link"]/a/@href').extract()[0]
        no = response.meta.get('index')
        base_url = get_base_url(response)
        image_url = urljoin(base_url, image_url)
        _, ext = image_url.split('/')[-1].split('.')
        image_name = u'{}.{}'.format(no, ext)
        path = self.PATH + '/' + remove_disallowed_filename_chars(image_name)
        if not exists(path):
            download(image_url, path)
