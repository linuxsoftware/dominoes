#---------------------------------------------------------------------------
# Testing Utilities needed to test the GameServer
#---------------------------------------------------------------------------
# Based on http://github.com/aio-libs/aioredis/blob/master/tests
#     also http://stackoverflow.com/questions/23033939

from functools import wraps
import asyncio
import unittest

def asynctest(*args):
    func = args[0] if len(args) else None
    if not asyncio.iscoroutinefunction(func):
        func = asyncio.coroutine(func)

    @wraps(func)
    def wrapper(test, *args, **kw):
        coro = asyncio.wait_for(func(test, *args, **kw), 15, loop=test.loop)
        ret = test.loop.run_until_complete(coro)
        return ret
    return wrapper


class UnitTestCase(unittest.TestCase):
    """Base test case for async unittests."""
    def setUp(self):
        super().setUp()
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self):
        super().tearDown()
        self.loop.close()
        del self.loop
