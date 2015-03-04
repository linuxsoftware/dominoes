# ------------------------------------------------------------------------------
# The Game
# ------------------------------------------------------------------------------

import sys
from enum import Enum
import asyncio
import inspect
from functools import wraps
from autobahn.wamp.exception import ApplicationError
from autobahn.wamp.exception import NotAuthorized
from autobahn.asyncio.wamp import ApplicationSession
from autobahn.asyncio.wamp import ApplicationSessionFactory
from autobahn import wamp
from autobahn.wamp.types import ComponentConfig
from autobahn.wamp.types import RegisterOptions
from autobahn.wamp.types import CallResult
from .rules import SolitaireRules
from .boneyard import Boneyard
from .players import Players
from .player import Player
#from .playingArea import PlayingArea
from .user import UserFactory
from .oauthuser import oauthWorkers
from .dbuser    import dbWorkers

import logging
log = logging.getLogger(__name__)

UserFactory.add(oauthWorkers)
UserFactory.add(dbWorkers)


def uri(suffix):
    return "nz.net.software.dominoes."+suffix

def register(uri):
    def wrapper(func):
        @wraps(func)
        @wamp.register(uri)
        @asyncio.coroutine
        def authenticated(self, dtl):
            #TODO only look up user on join?
            dtl.user = yield from UserFactory(self.app).make(dtl.authid)
            if not dtl.user:
                log.warning("Unauthorized access {}".format(dtl.authid))
                raise NotAuthorized(dtl.authid)
            dtl.login  = dtl.user.login
            dtl.player = self.players.get(dtl.login)
            retval = func(self, dtl)
            if asyncio.iscoroutine(retval):
                return (yield from retval)
            else:
                return retval
        return authenticated
    return wrapper

# ------------------------------------------------------------------------------
# GamePlay
# ------------------------------------------------------------------------------
class GamePlay:
    def __init__(self, session):
        self.session = session
        self.app     = session.app
        self.rules   = session.rules
        self.players = session.players
        self.waitFor = {"waiting for a game to start"} # TODO could be part of players?
        log.debug("Init GamePlay")

        # TODO just supporting Solitaire for now
        if not isinstance(self.rules, SolitaireRules):
            log.warning("Rules unknown for {}".format(self.rules))
            raise NotImplementedError("{} not supported yet".format(self.rules))
        self.rules.numPlayers = len(self.players)
        self.boneyard = Boneyard()
        self.startBone = None

    def start(self):
        log.debug("GamePlay.start")
        if self.session.status != self.session.Status.Started:
            log.error("Attempt to start playing in {}".format(self.status))
            raise ApplicationError(uri("notstarted"), self.status.name)
        self.waitFor = set(self.players.keys())
        self.boneyard.shuffle()
        # NB yeah only one player in Solitaire
        for player in self.players:
            player.select(self.rules.numBonesToDraw)
        self.startBone = self.boneyard.select()

    def stop(self):
        self.waitFor = {"waiting for a new game to start"}

    @register(uri("ready"))
    def onReadyToPlay(self, dtl):
        PlayStatus = Enum("PlayStatus", "wait play")
        log.debug("onReadyToPlay by {}".format(dtl.user))
        self.waitFor.discard(dtl.login)
        if dtl.player is None:
            log.error("Invalid user calling ready {}".format(dtl.login))
            raise ApplicationError(uri("invaliduser"))
        if self.waitFor:
            status = PlayStatus.wait
        else:
            self.session.publish(uri("go"),
                                 player = self.players.current.login)
            status = PlayStatus.play
        return CallResult(status.name,
                          player  = dtl.player.details(),
                          players = self.players.summary(),
                          start   = str(self.startBone))

    @register(uri("show"))
    def onShowBone(self, bone, dtl):
        log.debug("onShowBone by {}".format(dtl.user))
        if self.waitFor:
            raise ApplicationError(uri("wait"), len(self.waitFor))
        if dtl.player != self.players.current:
            raise ApplicationError(uri("notyourturn"), self.status.name)
        self.publish(uri("shown"),
                     player = self.players.current.login,
                     bone   = bone)

    @register(uri("play"))
    def onPlayBone(self, dtl):
        log.debug("onPlayBone by {}".format(dtl.user))
        log.debug(inspect.currentframe().f_code.co_name)

    @register(uri("pass"))
    def onPassTurn(self, dtl):
        log.debug("onPassTurn by {}".format(dtl.user))
        log.debug(inspect.currentframe().f_code.co_name)

    @register(uri("giveup"))
    def onGiveUp(self, dtl):
        log.debug("onGiveUp by {}".format(dtl.user))
        log.debug(inspect.currentframe().f_code.co_name)


# ------------------------------------------------------------------------------
# GameSession
# ------------------------------------------------------------------------------
# TODO split out a GameAdmin class from GameSession???!
class GameSession(ApplicationSession):
    Status = Enum("GameStatus", "Waiting Ready Started")

    def __init__(self, app, gameId):
        super().__init__(ComponentConfig("game{}".format(gameId)))
        self.app     = app
        self.gameId  = gameId
        self.rules   = SolitaireRules()
        self.players = Players(self.rules.maxPlayers)
        self.status  = self.Status.Waiting
        self.play    = GamePlay(self)
        log.debug("Init game#{}".format(self.gameId))

    @asyncio.coroutine
    def onJoin(self, dtl):
        log.debug("GameSession.onJoin")
        opts = RegisterOptions("dtl", discloseCaller=True)
        yield from self.register(self, options=opts)
        yield from self.register(self.play, options=opts)

    @register(uri("poke"))
    def onPoke(self, dtl):
        log.debug("onPoke by {}".format(dtl.user))
        self.doUpdate()

    @register(uri("join"))
    @asyncio.coroutine
    def onJoinGame(self, dtl):
        log.debug("onJoinGame by {}".format(dtl.user))
        if self.status in (self.Status.Waiting, self.Status.Ready):
            self.players.add(Player(dtl.user, self.play))
            if len(self.players) >= self.rules.minPlayers:
                self.status = self.Status.Ready
            if len(self.players) == self.rules.maxPlayers:
                self.status = self.Status.Started
                self.play.start()
            self.doUpdate()
        else:
            raise ApplicationError(uri("alreadystarted"), self.status.name)

    @register(uri("leave"))
    def onLeaveGame(self, dtl):
        log.debug("onLeaveGame by {}".format(dtl.user))
        if self.status in (self.Status.Waiting, self.Status.Ready):
            self.players.remove(dtl.login)
            if len(self.players) < self.rules.minPlayers:
                self.status = self.Status.Waiting
            self.doUpdate()
        else:
            raise ApplicationError(uri("alreadystarted"), self.status.name)

    @register(uri("kick"))
    def onKickPlayer(self, dtl):
        log.debug("onKickPlayer by {}".format(dtl.user))
        log.debug(inspect.currentframe().f_code.co_name)

    @register(uri("start"))
    def onStartGame(self, dtl):
        log.debug("onStartGame by {}".format(dtl.user))
        if dtl.user != self.players.head:
            raise ApplicationError(uri("denied"))
        if self.status != self.Status.Ready:
            raise ApplicationError(uri("notready"), self.status.name)
        self.status = self.Status.Started
        self.play.start()
        self.doUpdate()

    @register(uri("stop"))
    def onStopGame(self, dtl):
        log.debug("onStopGame by {}".format(dtl.user))
        log.debug(inspect.currentframe().f_code.co_name)

    @register(uri("giveup"))
    def onGiveUp(self, dtl):
        log.debug("onGiveUp by {}".format(dtl.user))
        log.debug(inspect.currentframe().f_code.co_name)

    def doUpdate(self):
        log.debug("doUpdate pub")
        self.publish(uri("update"),
                     status  = self.status.name,
                     rules   = self.rules.name,
                     players = self.players.summary())

# ------------------------------------------------------------------------------
# GameSessionFactory
# ------------------------------------------------------------------------------
class GameSessionFactory(ApplicationSessionFactory):
    def __init__(self, app):
        self.app = app

    def __call__(self, gameId):
        session = GameSession(self.app, gameId)
        return session

# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
