#---------------------------------------------------------------------------
# Custom webasset extensions
#---------------------------------------------------------------------------

import gzip
from webassets.filter import Filter
from webassets.bundle import Bundle
from webassets.merge import MemoryHunk

#---------------------------------------------------------------------------
# Filters
#---------------------------------------------------------------------------
def noop(_in, out, **kw):
    """The simplest possible custom filter"""
    out.write(_in.read())

#---------------------------------------------------------------------------
# Gzip Bundle
#---------------------------------------------------------------------------
class GzipHunk(MemoryHunk):
    def save(self, filename):
        super().save(filename)
        with open(filename+".gz", 'wb') as out:
            zipped = gzip.compress(self.data().encode('utf-8'))
            out.write(zipped)
            # WARNING: .gz files get left behind by the clean command
            # TODO: to fix that, monkey patch the clean command to call 
            # a delete method on the bundle

class GzipBundle(Bundle):
    """saves both gzipped and ungzipped versions of the file"""
    def _merge_and_apply(self, ctx, output, force, parent_debug=None,
                         parent_filters=None, extra_filters=None,
                         disable_cache=None):
        hunk = super()._merge_and_apply(ctx, output, force, parent_debug,
                                        parent_filters, extra_filters,
                                        disable_cache)
        if hunk: # TODO: and not ctx.debug: ????
            hunk = GzipHunk(hunk._data, hunk.files)
        return hunk

#---------------------------------------------------------------------------
#---------------------------------------------------------------------------
