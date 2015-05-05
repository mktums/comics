import string
import urllib2
import unicodedata
from os.path import exists
from urlparse import urlparse, parse_qs, urljoin
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.selector import Selector
from scrapy.utils.response import get_base_url

PATH = 'Archive/SequentialArt'


class SASpider(CrawlSpider):
    name = 'sa'
    start_urls = ['http://www.collectedcurios.com/sequentialart.php', ]
    allowed_domains = ['collectedcurios.com', ]
    rules = (
        Rule(SgmlLinkExtractor(
            allow=(r'sequentialart\.php\?s=\d+',)
        ), callback='parse_item', follow=True),
    )

    # noinspection PyMethodMayBeStatic
    def parse_item(self, response):
        comic_id = parse_qs(urlparse(response.url).query).get('s')[0]
        sel = Selector(response)
        img_data = sel.xpath('//img[@id="strip"]')
        image_url = img_data.xpath('./@src').extract()[0]
        base_url = get_base_url(response)
        image_url = urljoin(base_url, image_url)
        name, ext = image_url.split('/')[-1].split('.')
        image_name = '{}.{}'.format(comic_id, ext)
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
