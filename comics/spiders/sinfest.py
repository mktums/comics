from os.path import exists

from urlparse import urlparse
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.selector import Selector

from comics.utils import remove_disallowed_filename_chars, download


class SinfestSpider(CrawlSpider):
    PATH = 'Archive/SinFest'
    name = 'sinfest'
    start_urls = ['http://sinfest.net/archiveb.php', ]
    allowed_domains = ['sinfest.net', ]
    rules = (
        Rule(SgmlLinkExtractor(
            allow=(r'comicID=\d+',)
        ), callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        comic_id = urlparse(response.url)[4].split('=')[1]
        sel = Selector(response)
        img_data = sel.xpath('//table[@id="AutoNumber2"]/tr[3]/td/p/img')
        image_url = img_data.xpath('./@src').extract()[0]
        image_title = img_data.xpath('./@alt').extract()[0]
        name, ext = image_url.split('/')[-1].split('.')
        image_name = '{}.{}.{}.{}'.format(comic_id, name, image_title, ext)
        path = self.PATH + '/' + remove_disallowed_filename_chars(unicode(image_name))
        if not exists(path):
            return download(image_url, path)
