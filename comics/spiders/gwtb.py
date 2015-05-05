import re
import string
import urllib2
import unicodedata
from os.path import exists
from urlparse import urljoin
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.selector import Selector
from scrapy.utils.response import get_base_url

PATH = 'Archive/GWTB'


class GWTBSpider(CrawlSpider):
    name = 'gwtb'
    start_urls = ['http://www.blastwave-comic.com/index.php', ]
    allowed_domains = ['blastwave-comic.com', ]
    rules = (
        Rule(SgmlLinkExtractor(
            allow=(r'index\.php\?p=comic&nro=\d+',)
        ), callback='parse_item', follow=True),
    )

    # noinspection PyMethodMayBeStatic
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
        image_name = '{}.{}'.format(image_title, ext)
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
    validfilenamechars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    cleanedfilename = unicodedata.normalize('NFKD', filename).encode('ASCII', 'ignore')
    return ''.join(c for c in cleanedfilename if c in validfilenamechars)
