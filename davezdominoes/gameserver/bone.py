# ------------------------------------------------------------------------------
# Bone
# ------------------------------------------------------------------------------
from enum import Enum

Space = Enum("Space", "Boneyard Hand Board")

class Pos:
    def __init__(self, x=0, y=0, space=Space.Boneyard):
        self.xpos  = x
        self.ypos  = y
        self.space = space

    def __str__(self):
        return "{0.xpos},{0.ypos},{0.space.name}".format(self)

class Bone():
    def __init__(self, inside, outside):
        self.__inside  = inside
        self.__outside = outside
        self.__pos     = Pos()

    @property
    def inside(self):
        return self.__inside

    @property
    def outside(self):
        return self.__outside

    @property
    def isDouble(self):
        return self.__inside == self.__outside

    @property
    def points(self):
        return self.__inside + self.__outside

    def __int__(self):
        return self.points

    def __eq__(self, other):
        return (self.__inside  == other.__inside and
                self.__outside == other.__outside)

    def canAttachTo(self, other):
        return other.__outside in (self.__inside, self.__outside)

    @property
    def pos(self):
        return self.__pos

    def setPos(self, x, y, space):
        self.__pos = Pos(x, y, space)

    def rotate(self):
        self.__inside, self.__outside = self.__outside, self.__inside

    def glyph(self, horizontal=True):
        if horizontal:
            doubleZero = 0x1f031
        else:
            doubleZero = 0x1f063
        return chr(doubleZero + self.__inside * 7 + self.__outside)

    def __str__(self):
        return "{0.inside}|{0.outside}".format(self)

    def __repr__(self):
        return "{0.inside}|{0.outside}@{0.pos}".format(self)

