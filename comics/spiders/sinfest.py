# coding: utf-8
from os.path import exists

from urlparse import urljoin
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.selector import Selector
from scrapy.utils.response import get_base_url

from comics.utils import remove_disallowed_filename_chars, download


class SinfestSpider(CrawlSpider):
    PATH = 'Archive/SinFest'
    name = 'sinfest'
    start_urls = ['http://sinfest.net/archiveb.php', ]
    allowed_domains = ['sinfest.net', ]
    rules = (
        Rule(SgmlLinkExtractor(
            allow=(r'view\.php\?date=',)
        ), callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        base_url = get_base_url(response)
        sel = Selector(response)
        img_data = sel.xpath('//tbody[@class="style5"]/tr[2]/td/img')
        image_url = urljoin(base_url, img_data.xpath('./@src').extract()[0])
        image_title = img_data.xpath('./@alt').extract()[0]
        name, ext = image_url.split('/')[-1].split('.')
        image_name = u'{}.{}.{}'.format(name, image_title, ext)
        path = self.PATH + '/' + remove_disallowed_filename_chars(image_name)
        if not exists(path):
            return download(image_url, path)
