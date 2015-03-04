# ------------------------------------------------------------------------------
# User Resources
# ------------------------------------------------------------------------------
# TODO more code sharing between gamecoordinator and gameserver ?!

from . import monkey
import asyncio
from abc import ABCMeta, abstractmethod
from .session import UserSession

import logging
log = logging.getLogger(__name__)


# ------------------------------------------------------------------------------
# User base class
# ------------------------------------------------------------------------------
class User(metaclass = ABCMeta):
    """A player in the game"""
    loginMethod   = None

    def __init__(self, name=''):
        self.login          = name.lower()
        self.name           = name

    def __eq__(self, other):
        return self.login == other.login

    def __str__(self):
        return "{0.login} ({0.name})".format(self)

    @property
    def avatarUrl(self):
        return self.getAvatarUrl(16)

    @abstractmethod
    def getAvatarUrl(self, size):
        return "//:0"

# ------------------------------------------------------------------------------
# UserFactory - an abstract factory where users are created
# ------------------------------------------------------------------------------
class UserFactory:
    _workers = {}

    def __init__(self, app):
        self.app = app

    @classmethod
    def add(cls, team):
        cls._workers.update(team)

    @asyncio.coroutine
    def make(self, crumb):
        session  = UserSession(self.app)
        yield from session.load(crumb)
        loginMethod = session.get('loginMethod', "database")
        worker = self._workers.get(loginMethod)
        if worker:
            user = yield from worker(session)
            return user

# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
