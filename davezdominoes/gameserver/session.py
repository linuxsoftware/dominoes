# ------------------------------------------------------------------------------
# User Session
# ------------------------------------------------------------------------------

from . import monkey
import sys
from collections.abc import MutableMapping
from beaker.session import SignedCookie
import asyncio
import aiomcache

import logging
log = logging.getLogger(__name__)

class UserSession(MutableMapping):
    """Wraps together the Settings, Memcache and the sessionId"""
    def __init__(self, app, crumb=None):
        self.app   = app
        self.crumb = crumb
        self.data  = {}
        urlParts   = self.app.settings.get('session.url').split(':')
        self.mc    = aiomcache.Client(urlParts[0], int(urlParts[1]))

    @property
    def login(self):
        return self.get('auth.userid', "")

    @asyncio.coroutine
    def load(self, crumb=None):
        if crumb:
            self.crumb = crumb
        self.data = yield from self.mc.get(self._getSessId(), {})

    @asyncio.coroutine
    def save(self, crumb=None):
        if crumb:
            self.crumb = crumb
        yield from self.mc.set(self._getSessId(), self.data)

    def _getSessId(self):
        if self.crumb is None:
            raise KeyError("feed me a crumb please")
        secret = self.app.settings.get('session.secret')
        fancy  = SignedCookie(secret)
        icing  = fancy.value_decode(self.crumb)[0] or ""
        return bytes(icing + '_session', 'utf-8')

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value

    def __delitem__(self, key):
        del self.data[key]

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)
