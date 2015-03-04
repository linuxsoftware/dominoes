#---------------------------------------------------------------------------
# Common utility functions
#---------------------------------------------------------------------------

#---------------------------------------------------------------------------
# String/text functions
#---------------------------------------------------------------------------
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode

def addUrlQueryParams(url, *args, **kwargs):
    # pass via args if you care about ordering, kwargs if you don't
    scheme, host, path, semi, qs, frag = urlparse(url)
    params = parse_qsl(qs) + list(args) + list(kwargs.items())
    qs = urlencode(params, doseq=True)
    return urlunparse((scheme, host, path, semi, qs, frag))


#---------------------------------------------------------------------------
# borrowed from pyramid.scripts.pserve
#---------------------------------------------------------------------------
import threading

class LazyWriter:
    """
    File-like object that opens a file lazily when it is first written
    to.
    """
    def __init__(self, filename, mode='w'):
        self.filename = filename
        self.fileobj = None
        self.lock = threading.Lock()
        self.mode = mode

    def open(self):
        if self.fileobj is None:
            with self.lock:
                self.fileobj = open(self.filename, self.mode)
        return self.fileobj

    def close(self):
        fileobj = self.fileobj
        if fileobj is not None:
            fileobj.close()

    def __del__(self):
        self.close()

    def write(self, text):
        fileobj = self.open()
        fileobj.write(text)
        fileobj.flush()

    def writelines(self, text):
        fileobj = self.open()
        fileobj.writelines(text)
        fileobj.flush()

    def flush(self):
        self.open().flush()


