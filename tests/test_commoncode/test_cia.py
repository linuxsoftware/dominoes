#---------------------------------------------------------------------------
# Collections, Iterators, and Algorithms Unit Tests
#---------------------------------------------------------------------------

from ..testcase import TestCase
from flexmock import flexmock
from davezdominoes.commoncode.cia import PeekIter, LoopIter, PeekLoopIter

#---------------------------------------------------------------------------
class IteratorTests(TestCase):
    def setUp(self):
        self.leroy = flexmock(login="leroy", name="Leroy Michalke")
        self.ray   = flexmock(login="ray",   name="Ray Allan Williamson")
        self.al    = flexmock(login="al",    name="Al Langhamer")
        self.bill  = flexmock(login="bill",  name="Bill Gray")
        super().setUp()

    def test_peeking(self):
        folk = [self.leroy, self.ray, self.al, self.bill]
        pit = PeekIter(folk)
        self.assertIs(pit.current, self.leroy)
        next(pit)
        self.assertIs(pit.current, self.ray)
        next(pit)
        self.assertIs(pit.current, self.al)
        with self.assertRaises(StopIteration):
            pit.advanceTo(self.ray)
        with self.assertRaises(StopIteration):
            next(pit)

    def test_looping(self):
        folk = [self.leroy, self.ray, self.al, self.bill]
        lit = LoopIter(folk, self.al)
        team = [plyr for plyr in lit]
        self.assertCountEqual(team, folk)
        self.assertListEqual(team, [self.al, self.bill, self.leroy, self.ray])

    def test_peeking_looping(self):
        folk = [self.leroy, self.ray, self.al, self.bill]
        pit = PeekLoopIter(folk, continuous=True)
        first = next(pit)
        self.assertIs(pit.loop.collection, folk)
        self.assertIs(pit.loop.start, first)
        next(pit)
        self.assertIs(pit.current, self.al)
        pit.advanceTo(self.ray)
        self.assertIs(pit.current, self.ray)
        pit.advanceUntil(lambda x:x.login == 'bill')
        self.assertIs(pit.current, self.bill)

