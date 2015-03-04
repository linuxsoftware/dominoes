# ------------------------------------------------------------------------------
# Boneyard
# ------------------------------------------------------------------------------
#from collections import deque
from .bone import Bone
import random

class Boneyard:
    __justOne = object()

    def __init__(self, topDots=6):
        random.seed()
        self._bones = []   # TODO change to deque?
        for inside in range(0, topDots+1):
            for outside in range(0, inside+1):
                self._bones.append(Bone(inside, outside))

    def shuffle(self):
        random.shuffle(self._bones)

    def select(self, numBones=__justOne):
        if numBones is self.__justOne:
            return self._bones.pop()
        else:
            retval = self._bones[-numBones:]
            del self._bones[-numBones:]
            return retval

    def print(self):
        inside = 1
        for b in self._bones:
            if b.inside != inside:
                print()
                inside = b.inside
            print(b, end=" ")
        print("\n")

    def __str__(self):
        return ", ".join(map(str, self._bones))

    def __repr__(self):
        return "'{}'".format(self)

    def __len__(self):
        return len(self._bones)


