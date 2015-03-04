#---------------------------------------------------------------------------
# Players Unit tests
#---------------------------------------------------------------------------

from ..testcase import TestCase
from .helpers import asynctest, UnitTestCase
from flexmock import flexmock
from davezdominoes.gameserver.player import Player
from davezdominoes.gameserver.bone   import Bone
from davezdominoes.gameserver.boneyard import Boneyard

#---------------------------------------------------------------------------
class PlayerTests(TestCase):
    def setUp(self):
        bones = ["3|4", "9|1", "4|6"]
        self.play  = flexmock(boneyard = flexmock(select = lambda n: bones))
        self.manny = flexmock(login     = "github:surfking",
                              name      = "Manny Bianco",
                              avatarUrl = "https://avatars2.githubusercontent"
                                          ".com/u/344?v=3")
        self.jack  = flexmock(login     = "jack",
                              name      = "Jack Parker",
                              avatarUrl = "//gravatar.com/avatar/"
                                          "514d2e5657f6f6ac1e122fce16fd72a3"
                                          "?d=wavatar&s=16")
        super().setUp()

    def test_init(self):
        manny = Player(self.manny, self.play)
        self.assertEqual(len(manny.hand), 0)

    def test_summary(self):
        manny = Player(self.manny, self.play)
        self.assertListEqual(manny.summary(),
                             ["github:surfking", "Manny Bianco",
                              self.manny.avatarUrl, 0])
        manny.select(3)
        self.assertListEqual(manny.summary(),
                             ["github:surfking", "Manny Bianco",
                              self.manny.avatarUrl, 3])

    def test_details(self):
        manny = Player(self.manny, self.play)
        manny.select(3)
        self.assertListEqual(manny.details(),
                             ["github:surfking", "Manny Bianco",
                              self.manny.avatarUrl,
                              ["3|4", "9|1", "4|6"]])


#---------------------------------------------------------------------------
#---------------------------------------------------------------------------
#---------------------------------------------------------------------------
