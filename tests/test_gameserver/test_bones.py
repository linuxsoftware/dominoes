#---------------------------------------------------------------------------
# Bones Unit tests
#---------------------------------------------------------------------------

from ..testcase import TestCase
from davezdominoes.gameserver.bone import Bone
from davezdominoes.gameserver.boneyard import Boneyard

#---------------------------------------------------------------------------
class BoneTests(TestCase):
    def test_initBone(self):
        bone = Bone(2,3)
        self.assertEqual(bone.inside, 2)
        self.assertEqual(bone.outside, 3)
        self.assertFalse(bone.isDouble)
        self.assertEqual(bone.points, 5)
        self.assertEqual(str(bone), "2|3")

#---------------------------------------------------------------------------
class BoneyardTests(TestCase):
    def test_initBoneyard(self):
        boneyard = Boneyard()
        self.assertEqual(len(boneyard), 28)
        self.assertEqual(str(boneyard)[:14], "0|0, 1|0, 1|1,")
        self.assertEqual(boneyard.select().points, 12)
        self.assertListEqual(boneyard.select(2), [Bone(6,4), Bone(6,5)])

    def test_select(self):
        boney = Boneyard(12)
        self.assertEqual(len(boney), 91)
        s = Bone(12, 12)
        p1 = boney.select(9)
        self.assertIn(s, p1)
        self.assertEqual(len(p1), 9)
        self.assertEqual(len(boney), 82)
        p2 = boney.select(9)
        self.assertNotIn(s, p2)
        self.assertEqual(len(boney), 73)
        p3 = boney.select(9)
        self.assertNotIn(s, p3)
        self.assertEqual(len(boney), 64)
        p4 = boney.select(9)
        self.assertNotIn(s, p4)
        self.assertEqual(len(boney), 55)

#---------------------------------------------------------------------------
#---------------------------------------------------------------------------
