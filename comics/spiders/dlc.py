# coding: utf-8
from os.path import exists
from urlparse import urljoin
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.selector import Selector
from scrapy.utils.response import get_base_url
from comics.utils import remove_disallowed_filename_chars, download


class DLCSpider(CrawlSpider):
    PATH = 'Archive/DarkLegacyComics'
    name = 'dlc'
    start_urls = ['http://www.darklegacycomics.com/archive', ]
    allowed_domains = ['www.darklegacycomics.com', ]
    rules = (
        Rule(SgmlLinkExtractor(
            allow=(r'darklegacycomics.com/\d+$',),
            deny=(
                # These aren't comics :)
                r'darklegacycomics.com/209$',
                r'darklegacycomics.com/186$'
            ),
        ), callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        sel = Selector(response)
        base_url = get_base_url(response)
        no = response.url.rsplit('/')[-1]
        image_title = response.meta.get('link_text')
        image_url = sel.xpath('//img[@class="comic-image"]/@src').extract()[0]
        image_url = urljoin(base_url, image_url)
        _, ext = image_url.split('/')[-1].rsplit('.', 1)
        image_name = u'{}.{}.{}'.format(no, image_title, ext)
        path = self.PATH + '/' + remove_disallowed_filename_chars(image_name)
        if not exists(path):
            return download(image_url, path)