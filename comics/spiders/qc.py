# coding: utf-8
from os.path import exists
from urlparse import urljoin
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.selector import Selector
from scrapy.utils.response import get_base_url
from comics.utils import remove_disallowed_filename_chars, download


class YAFGCSpider(CrawlSpider):
    PATH = 'Archive/QuestionableContent'
    name = 'qc'
    start_urls = ['http://questionablecontent.net/archive.php', ]
    allowed_domains = ['questionablecontent.net', ]
    rules = (
        Rule(SgmlLinkExtractor(allow=(r'view\.php\?comic=\d+$',)), callback='parse_item'),
    )

    def parse_start_url(self, response):
        self.cookie = response.headers.get('Set-Cookie').split(';', 1)[0]
        return super(YAFGCSpider, self).parse_start_url(response)

    def parse_item(self, response):
        sel = Selector(response)
        no, image_name = response.meta.get('link_text').split(': ', 1)
        no = no.replace('Comic ', '')
        image_url = sel.xpath('//img[@id="strip"]/@src').extract()[0]
        base_url = get_base_url(response)
        image_url = urljoin(base_url, image_url)
        _, ext = image_url.split('/')[-1].rsplit('.', 1)
        image_name = u'{}.{}.{}'.format(no, image_name, ext)
        path = self.PATH + '/' + remove_disallowed_filename_chars(image_name)
        if not exists(path):
            return download(image_url, path, response.url, self.cookie)
