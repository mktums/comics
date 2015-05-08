from os.path import exists

from dateutil.parser import parse as date_parser
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.selector import Selector

from comics.utils import remove_disallowed_filename_chars, download


class YAFGCSpider(CrawlSpider):
    PATH = 'Archive/YAFGC'
    name = 'yafgc'
    start_urls = ['http://yafgc.net/archive.php', ]
    allowed_domains = ['yafgc.net', ]
    rules = (
        Rule(SgmlLinkExtractor(allow=(r'archive\.php\?arc=',))),
        Rule(SgmlLinkExtractor(
            allow=(r'\?id=\d+$',),
            deny=(
                r'purchaseprints\.php',
                r'news\.php',
            ),
        ), callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        sel = Selector(response)
        img_data = sel.xpath('//div[@id="comicset"]')
        image_date = [x.strip() for x in img_data.xpath('./text()').extract() if x.strip()][0]
        image_date = ', '.join([x.strip() for x in image_date.split(',')[1:]]).replace('Febuary', 'February')
        full_title = img_data.xpath('./h2/text()').extract()[0]
        no, image_title = full_title.split(':', 1)
        no = no.split()[1]
        if image_title[-1] == '.' and not image_title[-2] == '.':
            image_title = image_title[:-1]
        image_url = img_data.xpath('//img[@id="comicimg"]/@src').extract()[0]
        name, ext = image_url.split('/')[-1].split('.')
        image_name = '{}.{}.{}.{}'.format(no, date_parser(image_date).strftime('%Y-%m-%d'), image_title.strip(), ext)
        path = self.PATH + '/' + remove_disallowed_filename_chars(unicode(image_name))
        if not exists(path):
            return download(image_url, path)
