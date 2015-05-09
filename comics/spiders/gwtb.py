# coding: utf-8
import re
from os.path import exists
from urlparse import urljoin

from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.selector import Selector
from scrapy.utils.response import get_base_url

from comics.utils import download, remove_disallowed_filename_chars


class GWTBSpider(CrawlSpider):
    PATH = 'Archive/GWTB'
    name = 'gwtb'
    start_urls = ['http://www.blastwave-comic.com/index.php', ]
    allowed_domains = ['blastwave-comic.com', ]
    rules = (
        Rule(SgmlLinkExtractor(
            allow=(r'index\.php\?p=comic&nro=\d+',)
        ), callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        sel = Selector(response)
        img_data = sel.xpath('//td[@id="comic_ruutu"]')
        image_title = img_data.xpath('./center/div/text()').extract()[0]
        image_title = re.sub(r'^[#*](\d+)\s+', '\g<1>. ', image_title)
        if image_title[-1] == '.' and not image_title[-2] == '.':
            image_title = image_title[:-1]
        base_url = get_base_url(response)
        image_url = urljoin(base_url, img_data.xpath('./center/img/@src').extract()[0])
        name, ext = image_url.split('/')[-1].split('.')
        image_name = u'{}.{}'.format(image_title, ext)
        path = self.PATH + '/' + remove_disallowed_filename_chars(image_name)
        if not exists(path):
            return download(image_url, path)
