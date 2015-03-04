#---------------------------------------------------------------------------
# Monkey patches make me sad :-(
#---------------------------------------------------------------------------

# TODO maybe I should just fork aiomcache?!

import asyncio
from io import BytesIO
import pickle
from aiomcache import Client
from aiomcache.exceptions import ClientException, ValidationException
from aiomcache.client     import acquire

@asyncio.coroutine
def monkey_mc_multi_get(self, reader, writer, *keys):
    # req  - get <key> [<key> ...]\r\n
    # resp - VALUE <key> <flags> <bytes> [<cas unique>]\r\n
    #        <data block>\r\n (if exists)
    #        [...]
    #        END\r\n
    if not keys:
        return []

    [self._validate_key(key) for key in keys]
    if len(set(keys)) != len(keys):
        raise ClientException('duplicate keys passed to multi_get')

    writer.write(b'get ' + b' '.join(keys) + b'\r\n')

    received = {}
    line = yield from reader.readline()

    while line != b'END\r\n':
        terms = line.split()

        if len(terms) == 4 and terms[0] == b'VALUE': # exists
            key = terms[1]
            flags = int(terms[2])
            length = int(terms[3])

            if flags > 1:
                raise ClientException('received unknown flags')

            val = (yield from reader.readexactly(length+2))[:-2]
            if key in received:
                raise ClientException('duplicate results from server')

            if flags == 1:
                val = pickle.loads(val)
                # How to check a pickle's protocol :-)
                #unpickler = pickle._Unpickler(BytesIO(val))
                #val = unpickler.load()
                #print("PROTO ", unpickler.proto)
            received[key] = val
        else:
            raise ClientException('get failed', line)

        line = yield from reader.readline()

    if len(received) > len(keys):
        raise ClientException('received too many responses')

    # memcache client is used by other servers besides memcached.
    # In the case of kestrel, responses coming back to not necessarily
    # match the requests going out. Thus we just ignore the key name
    # if there is only one key and return what we received.
    if len(keys) == 1 and len(received) == 1:
        response = list(received.values())
    else:
        response = [received.get(key) for key in keys if key in received]

    return response

Client._multi_get = monkey_mc_multi_get

@acquire
def monkey_json_set(self, reader, writer,  key, val, exptime=0):
    """Sets a key to a value on the server
    with an optional exptime (0 means don't auto-expire)
    """
    if isinstance(val, bytes):
        yield from self._set_bytes(reader, writer, key, val, exptime)
    else:
        yield from self._set_pickle(reader, writer, key, val, exptime)

def monkey_json_set_pickle(self, reader, writer,  key, val, exptime=0):
    assert self._validate_key(key)
    # req  - set <key> <flags> <exptime> <bytes> [noreply]\r\n
    #        <data block>\r\n
    # resp - STORED\r\n (or others)

    # typically, if val is > 1024**2 bytes server returns:
    #   SERVER_ERROR object too large for cache\r\n
    # however custom-compiled memcached can have different limit
    # so, we'll let the server decide what's too much

    if not isinstance(exptime, int):
        raise ValidationException('exptime not int', exptime)
    elif exptime < 0:
        raise ValidationException('exptime negative', exptime)

    val = pickle.dumps(val, protocol=0)
    writer.write(b''.join((b'set ', key, b' 1 ',
                           ('%d %d' % (exptime, len(val))).encode('utf-8'),
                           b'\r\n', val, b'\r\n')))

    resp = yield from reader.readline()
    if resp != b'STORED\r\n':
        raise ClientException('set failed', resp)

Client.set = monkey_json_set
Client._set_bytes = Client.set
Client._set_pickle = monkey_json_set_pickle



