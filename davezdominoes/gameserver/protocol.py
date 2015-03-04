# ------------------------------------------------------------------------------
# Dominoes Protocol Customization
# ------------------------------------------------------------------------------

import sys
from autobahn.asyncio.wamp import RouterSession
from autobahn.asyncio.websocket import WampWebSocketServerProtocol
from autobahn.wamp.types import Accept, Deny
from http.cookies import SimpleCookie
from .session import UserSession
import asyncio

import logging
log = logging.getLogger(__name__)


def getCrumb(app, request):
    cookie = request.headers.get('cookie')
    plain  = SimpleCookie(cookie)
    key    = app.settings.get('session.key')
    morsel = plain.get(key)
    if morsel:
        return morsel.value

class DominoesProtocol(WampWebSocketServerProtocol):
    def onConnect(self, request):
        log.info("DominoesProtocol.onConnect")
        protocol, headers = super().onConnect(request)
        self.crumb = getCrumb(self.factory.app, request)
        return (protocol, headers)

class DominoesRouterSession(RouterSession):
    def onOpen(self, transport):
        super().onOpen(transport)
        log.debug("DominoesRouterSession.onOpen")

    @asyncio.coroutine
    def onHello(self, realm, dtl):
        log.debug("DominoesRouterSession.onHello: {} {}".format(realm, dtl))
        authmethods = dtl.authmethods or []
        if "beaker" in authmethods:
            session = UserSession(self._transport.factory.app)
            yield from session.load(self._transport.crumb)
            userId = session.login
            if userId:
                # it's still fresh, save the crumb
                log.debug("authenticated {}".format(userId))
                return Accept(authid     = self._transport.crumb,
                              authmethod = 'beaker')
        else:
            return Deny()

    def onJoin(self, dtl):
        log.debug("DominoesRouterSession.onJoin: {}".format(dtl))

    def onLeave(self, dtl):
        log.debug("DominoesRouterSession.onLeave: {}".format(dtl))

