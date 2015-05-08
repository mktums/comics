import string
import unicodedata
import urllib2


def download(url, file_name):
    u = urllib2.urlopen(url)
    f = open(file_name, 'wb')
    meta = u.info()
    file_size = int(meta.getheaders("Content-Length")[0])
    print "Downloading: %s Bytes: %s" % (file_name, file_size)

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
