#---------------------------------------------------------------------------
# Players Unit tests
#---------------------------------------------------------------------------

from ..testcase import TestCase
from .helpers import asynctest, UnitTestCase
import asyncio
from flexmock import flexmock
from davezdominoes.gameserver.players import _PlayerMap
from davezdominoes.gameserver.players import Players

#---------------------------------------------------------------------------
class PlayerMapTests(TestCase):
    def setUp(self):
        self.leroy = flexmock(login="leroy", name="Leroy Michalke")
        self.ray   = flexmock(login="ray",   name="Ray Allan Williamson")
        self.al    = flexmock(login="al",    name="Al Langhamer")
        self.bill  = flexmock(login="bill",  name="Bill Gray")
        self.players = [self.leroy, self.ray, self.al, self.bill]
        super().setUp()

    def test_getLink(self):
        playerMap = _PlayerMap((plyr.login, plyr) for plyr in self.players)
        link = playerMap.getLink('al')
        self.assertIs(link.this, self.al)
        self.assertIs(link.prev, self.ray)
        self.assertIs(link.next, self.bill)

    def test_getFirstLink(self):
        playerMap = _PlayerMap((plyr.login, plyr) for plyr in self.players)
        link = playerMap.getLink('leroy')
        self.assertIs(link.this, self.leroy)
        self.assertIs(link.prev, self.bill)
        self.assertIs(link.next, self.ray)

    def test_getLastLink(self):
        playerMap = _PlayerMap((plyr.login, plyr) for plyr in self.players)
        link = playerMap.getLink('bill')
        self.assertIs(link.this, self.bill)
        self.assertIs(link.prev, self.al)
        self.assertIs(link.next, self.leroy)

    def test_getMissingLink(self):
        playerMap = _PlayerMap((plyr.login, plyr) for plyr in self.players)
        self.assertEqual(playerMap.getLink('sedrick', "rubarb"), "rubarb")
        self.assertIsNone(playerMap.getLink('sedrick'))

#---------------------------------------------------------------------------
class PlayersTests(TestCase):
    def setUp(self):
        self.leroy = flexmock(login="leroy", name="Leroy Michalke")
        self.ray   = flexmock(login="ray",   name="Ray Allan Williamson")
        self.al    = flexmock(login="al",    name="Al Langhamer")
        self.bill  = flexmock(login="bill",  name="Bill Gray")
        super().setUp()

    def test_init(self):
        players = Players()
        self.assertEqual(len(players), 0)
        self.assertNotIn('sedrick', players)
        self.assertIsNone(players.get('sedrick'))
        players.remove('sedrick')
        players.clear()

    def test_initWithMax(self):
        players = Players(maxPlayers=2)
        self.assertEqual(len(players), 0)
        players.add(self.leroy)
        self.assertEqual(len(players), 1)
        players.add(self.ray)
        players.add(self.al)
        self.assertEqual(len(players), 2)
        self.assertNotIn('al', players)

    def test_add_get_remove(self):
        players = Players()
        players.add(self.leroy)
        self.assertIs(players.get('leroy'), self.leroy)
        players.add(self.al)
        self.assertEqual(players.current.login, 'leroy')
        self.assertEqual(players.start.login, 'leroy')
        players.remove('leroy')
        self.assertEqual(players.current.login, 'al')
        self.assertEqual(players.start.login, 'al')

    def test_turnIter(self):
        players = Players()
        players.add(self.leroy)
        players.add(self.ray)
        players.add(self.al)
        self.assertEqual(players.current.login, 'leroy')
        self.assertEqual(players.current.login, 'leroy')
        players.next()
        self.assertEqual(players.current.login, 'ray')
        for i in range(len(players)+1):
            players.next()
        self.assertEqual(players.current.login, 'al')

#---------------------------------------------------------------------------
#---------------------------------------------------------------------------
#---------------------------------------------------------------------------
