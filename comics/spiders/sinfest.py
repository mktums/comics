import string
import urllib2
import unicodedata
from os.path import exists
from urlparse import urlparse
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.selector import Selector

PATH = 'Archive/SinFest'


class SinfestSpider(CrawlSpider):
    name = 'sinfest'
    start_urls = ['http://sinfest.net/archiveb.php', ]
    allowed_domains = ['sinfest.net', ]
    rules = (
        Rule(SgmlLinkExtractor(
            allow=(r'comicID=\d+',)
        ), callback='parse_item', follow=True),
    )

    # noinspection PyMethodMayBeStatic
    def parse_item(self, response):
        comic_id = urlparse(response.url)[4].split('=')[1]
        sel = Selector(response)
        img_data = sel.xpath('//table[@id="AutoNumber2"]/tr[3]/td/p/img')
        image_url = img_data.xpath('./@src').extract()[0]
        image_title = img_data.xpath('./@alt').extract()[0]
        name, ext = image_url.split('/')[-1].split('.')
        image_name = '{}.{}.{}.{}'.format(comic_id, name, image_title, ext)
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
