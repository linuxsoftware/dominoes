# ------------------------------------------------------------------------------
# Player Resource
# ------------------------------------------------------------------------------

import sys
from .bone     import Bone
from .boneyard import Boneyard

import logging
log = logging.getLogger(__name__)


class Player:
    def __init__(self, user, play):
        self.user  = user
        self.game  = play
        self.hand  = []

    @property
    def login(self):
        return self.user.login

    @property
    def name(self):
        return self.user.name

    @property
    def avatarUrl(self):
        return self.user.avatarUrl

    @property
    def points(self):
        return sum(self.hand)

    def __eq__(self, other):
        return self.login == other.login

    def __str__(self):
        return str(self.user)

    def select(self, numBones=1):
        bones = self.game.boneyard.select(numBones)
        # set positions on bones
        #for i, bone in enumerate(bones, len(self.hand)):
        #    bone.setPos(i*60+10, 470, Pos.Space.Hand)
        self.hand.extend(bones)

    def summary(self):
        """list of properties about this player for other players to see"""
        return [self.login, self.name, self.avatarUrl, len(self.hand)]

    def details(self):
        """list of properties about this player, including bones in hand"""
        hand = [str(bone) for bone in self.hand]
        return [self.login, self.name, self.avatarUrl, hand]

# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
