# coding: utf-8
from os.path import exists

from urlparse import urlparse, parse_qs, urljoin
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.selector import Selector
from scrapy.utils.response import get_base_url

from comics.utils import remove_disallowed_filename_chars, download


class SASpider(CrawlSpider):
    PATH = 'Archive/SequentialArt'
    name = 'sa'
    start_urls = ['http://www.collectedcurios.com/sequentialart.php', ]
    allowed_domains = ['collectedcurios.com', ]
    rules = (
        Rule(SgmlLinkExtractor(
            allow=(r'sequentialart\.php\?s=\d+',)
        ), callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        comic_id = parse_qs(urlparse(response.url).query).get('s')[0]
        sel = Selector(response)
        img_data = sel.xpath('//img[@id="strip"]')
        image_url = img_data.xpath('./@src').extract()[0]
        base_url = get_base_url(response)
        image_url = urljoin(base_url, image_url)
        name, ext = image_url.split('/')[-1].split('.')
        image_name = u'{}.{}'.format(comic_id, ext)
        path = self.PATH + '/' + remove_disallowed_filename_chars(image_name)
        if not exists(path):
            return download(image_url, path)
