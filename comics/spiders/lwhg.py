# coding: utf-8
from os.path import exists

from urlparse import urljoin
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.selector import Selector
from scrapy.utils.response import get_base_url

from comics.utils import remove_disallowed_filename_chars, download


class LWHGSpider(CrawlSpider):
    PATH = 'Archive/LWHG'
    name = 'lwhg'
    start_urls = ['http://www.jagodibuja.com/webcomic-living-with-hipstergirl-and-gamergirl-english/', ]
    allowed_domains = ['jagodibuja.com', ]
    rules = (
        Rule(SgmlLinkExtractor(
            allow=(r'/webcomic-living-with-hipstergirl-and-gamergirl-english/.+/$',),
            deny=(r'/feed/$',),
        ), callback='parse_item', follow=True),
    )

    def parse_start_url(self, response):
        image_url = Selector(response).xpath('//div[@class="entry-content"]/p/a/@href').extract()[0]
        base_url = get_base_url(response)
        image_url = urljoin(base_url, image_url)
        _, ext = image_url.split('/')[-1].split('.')
        image_name = u'_characters.{}'.format(ext)
        path = self.PATH + '/' + remove_disallowed_filename_chars(image_name)
        if not exists(path):
            download(image_url, path)
        return super(LWHGSpider, self).parse_start_url(response)

    def parse_item(self, response):
        sel = Selector(response)
        image_url = sel.xpath('//span[@class="full-size-link"]/a/@href').extract()[0]
        no = filter(unicode.isdigit, sel.xpath('//h1/text()').extract()[0])
        base_url = get_base_url(response)
        image_url = urljoin(base_url, image_url)
        _, ext = image_url.split('/')[-1].split('.')
        image_name = u'{}.{}'.format(no, ext)
        path = self.PATH + '/' + remove_disallowed_filename_chars(image_name)
        if not exists(path):
            download(image_url, path)
