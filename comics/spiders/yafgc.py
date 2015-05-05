import string
import urllib2
import unicodedata
from os.path import exists
from dateutil.parser import parse as date_parser
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.selector import Selector


PATH = 'Archive/YAFGC'


class YAFGCSpider(CrawlSpider):
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

    # noinspection PyMethodMayBeStatic
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
        path = PATH + '/' + remove_disallowed_filename_chars(unicode(image_name))
        if not exists(path):
            return download(image_url, path)


def download(url, file_name):
    u = urllib2.urlopen(url)
    f = open(file_name, 'wb')
    meta = u.info()
    file_size = int(meta.getheaders("Content-Length")[0])
    print "Downloading: %s Bytes: %s" % (file_name, file_size)

    file_size_dl = 0
    block_sz = 8192
    while True:
        buffer = u.read(block_sz)
        if not buffer:
            break

        file_size_dl += len(buffer)
        f.write(buffer)
        status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
        status += chr(8) * (len(status) + 1)
        print status,

    f.close()


def remove_disallowed_filename_chars(filename):
    validFilenameChars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    cleanedFilename = unicodedata.normalize('NFKD', filename).encode('ASCII', 'ignore')
    return ''.join(c for c in cleanedFilename if c in validFilenameChars)
