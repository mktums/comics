# coding: utf-8
import string
import unicodedata
import urllib2
import urlparse
from comics.settings import USER_AGENT


def download(url, file_name, referer=None, cookie=None):
    data = urlparse.urlparse(url)
    data._replace(path=urllib2.quote(data.path.encode('utf-8')))
    url = data.geturl().encode('utf-8')
    req = urllib2.Request(url)
    if referer:
        req.add_header("Referer", referer)
    if cookie:
        req.add_header("Cookie", cookie)
    req.add_header("User-Agent", USER_AGENT)
    u = urllib2.urlopen(req)
    f = open(file_name, 'wb')
    meta = u.info()
    file_size = int(meta.getheaders("Content-Length")[0])
    print u"Downloading: %s Bytes: %s" % (file_name, file_size)

    file_size_dl = 0
    block_sz = 8192
    while True:
        _buffer = u.read(block_sz)
        if not _buffer:
            break

        file_size_dl += len(_buffer)
        f.write(_buffer)
        status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
        status += chr(8) * (len(status) + 1)
        print status,

    f.close()


def remove_disallowed_filename_chars(filename):
    validfilenamechars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    cleanedfilename = unicodedata.normalize('NFKD', filename).encode('ASCII', 'ignore')
    return ''.join(c for c in cleanedfilename if c in validfilenamechars)
