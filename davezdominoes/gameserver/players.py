# ------------------------------------------------------------------------------
# Players
# ------------------------------------------------------------------------------

import sys
import json
from collections.abc import Sized, Iterable, Container
from collections import namedtuple, OrderedDict
from ..commoncode.cia import PeekLoopIter

import logging
log = logging.getLogger(__name__)


# Ugly! Ugly! UGLY! OrderedDict needs to share a bit more of its internals
# TODO or should I just replace it completely with my own data structure?
# TODO see also http://code.activestate.com/recipes/576694/
class _PlayerMap(OrderedDict):
    PlayerLink = namedtuple("PlayerLink", "prev next this")
    def getLink(self, key, default=None):
        link = self._OrderedDict__map.get(key, default)
        if link is default:
            return link
        if link.prev is self._OrderedDict__root:
            prevKey = link.prev.prev.key
        else:
            prevKey = link.prev.key
        if link.next is self._OrderedDict__root:
            nextKey = link.next.next.key
        else:
            nextKey = link.next.key
        return self.PlayerLink(self[prevKey], self[nextKey], self[link.key])


class Players(Sized, Iterable, Container):
    """A collection of the players in a game, indexed by login"""
    def __init__(self, maxPlayers=16):
        self.maxPlayers = maxPlayers
        self._players   = _PlayerMap()
        self._turnIter  = None

    def __len__(self):                                # Sized
        return len(self._players)

    def __iter__(self):                               # Iterable
        return iter(self._players.values())

    def __contains__(self, login):                    # Container
        return login in self._players

    def keys(self):
        return self._players.keys()

    def add(self, player):
        if (len(self._players) < self.maxPlayers or
                player.login in self._players):
            self._players[player.login] = player
            if len(self._players) == 1:
                self._turnIter = PeekLoopIter(self._players.values(),
                                              continuous=True)

    def update(self, player):
        if player.login in self._players:
            self._players[player.login] = player

    def remove(self, login):
        link = self._players.getLink(login, None)
        if link is None:
            return
        if link.this == self._turnIter.current:
            next(self._turnIter)
        if link.this == self._turnIter.loop.start:
            self._turnIter.loop.start = link.next
        del self._players[login]

    def clear(self):
        self._players.clear()
        self._turnIter = None

    def get(self, login, default=None):
        return self._players.get(login, default)

    @property
    def head(self):
        return next(iter(self._players.values()), None)

    @property
    def current(self):
        if self._turnIter:
            return self._turnIter.current

    @property
    def start(self):
        if self._turnIter:
            return self._turnIter.loop.start

    def next(self):
        # not a proper iterator interface, but everyone still gets their turn
        if self._turnIter:
            return next(self._turnIter)

    def roundIter(self):
        roundIt = PeekLoopIter(self._players.values(), self.start)
        return roundIt

    def summary(self):
        return [player.summary() for player in self._players.values()]
