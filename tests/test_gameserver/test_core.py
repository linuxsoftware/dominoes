#---------------------------------------------------------------------------
# Core tests
#---------------------------------------------------------------------------

from ..testcase import TestCase
from .helpers import asynctest, UnitTestCase
import asyncio
from flexmock import flexmock
from davezdominoes.gameserver.protocol import getCrumb
from davezdominoes.gameserver.session import UserSession

#---------------------------------------------------------------------------
class CrumbTests(TestCase):
    def test_getCrumb(self):
        app = flexmock(settings={'session.key': "chubby"})
        req = flexmock(headers={'cookie': "foo=bar;chubby=dadaddadumdaadaada"})
        self.assertEqual(getCrumb(app, req), "dadaddadumdaadaada")
        req = flexmock(headers={})
        self.assertIsNone(getCrumb(app, req))

#---------------------------------------------------------------------------
class UserSessionTests(UnitTestCase):
    def setUp(self):
        self.app = flexmock(settings={'session.url':    "10.20.30.40:22322",
                                      'session.key':    "chubby",
                                      'session.secret': "badjelly"})
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_init(self):
        session = UserSession(self.app)
        self.assertEqual(len(session), 0)
        self.assertIs(session.app, self.app)
        self.assertEqual(session.mc._pool._host, "10.20.30.40")
        self.assertEqual(session.mc._pool._port, 22322)
        self.assertFalse('caramel' in session)
        self.assertEqual(session.get('caramel', 'rumraisin'), 'rumraisin')
        with self.assertRaises(KeyError):
            del session['nuts']

    def test_put_get_del(self):
        session = UserSession(self.app)
        session['dried.fruit'] = 'sultana'
        self.assertTrue('dried.fruit' in session)
        with self.assertRaises(KeyError):
            session['nuts']
        self.assertIsNone(session.get('nuts'))
        self.assertEqual(session.get('dried.fruit', 'raisin'), 'sultana')
        self.assertEqual(session['dried.fruit'], 'sultana')
        del session['dried.fruit']
        self.assertTrue('dried.fruit' not in session)
        session.clear()

    @asynctest
    def test_load_save(self):
        session = UserSession(self.app)
        sessId = b'10eab75f2c18461f9981da8c2e6e2101_session'
        fakeCache = {'dried.fruit': 'sultana',
                     'bread':       ['sunflower', 'barley'],
                     'meat':        'lamb'}
        @asyncio.coroutine
        def fakeGet(crumb, default=None):
            self.assertEqual(crumb, sessId)
            return fakeCache
        session.mc.get = fakeGet
        @asyncio.coroutine
        def fakeSet(crumb, data):
            self.assertEqual(crumb, sessId)
            fakeCache = data
            return fakeCache
        session.mc.set = fakeSet
        yield from session.load("316ae9453d6c9bcfbe8610a30e07ad248a37"
                                "602d10eab75f2c18461f9981da8c2e6e2101")
        self.assertEqual(session['dried.fruit'], "sultana")
        self.assertEqual(session['bread'], ["sunflower", "barley"])
        self.assertEqual(session.get('meat'), "lamb")
        session['bread'] = "rye"
        session['salad'] = "caesar"
        yield from session.save()
        self.assertEqual(len(fakeCache), 4)
        self.assertEqual(fakeCache['dried.fruit'], "sultana")
        self.assertEqual(fakeCache['bread'], "rye")
        self.assertEqual(fakeCache['salad'], "caesar")


#---------------------------------------------------------------------------
#---------------------------------------------------------------------------
#---------------------------------------------------------------------------
