# ------------------------------------------------------------------------------
# GameServer App
# ------------------------------------------------------------------------------

from . import monkey
import os
import sys
from argparse import ArgumentParser
from pprint import pprint
from pathlib import Path
import asyncio
from aiopg.sa import create_engine
from sqlalchemy.engine.url import make_url
from autobahn.asyncio.wamp import RouterFactory
from autobahn.asyncio.wamp import RouterSessionFactory
from autobahn.asyncio.websocket import WampWebSocketServerFactory
from paste.deploy import appconfig
from pyramid.settings import asbool
from logging.config import fileConfig
from .protocol import DominoesProtocol, DominoesRouterSession
from .game import GameSessionFactory
from secret import SessionKey
from ..commoncode.proc import DaemonHandle
from ..commoncode.utils import LazyWriter

import logging


class DominoesApp():
    """Main class to host the Dominoes GameServer (WAMP Router+Application)"""
    # The DominoesApp class contains the configuration information for
    # DavezDominoes, but should not be confused with SessionConfig.

    def __init__(self, confFile):
        self.transportFactory = None
        self.sessionFactory   = None
        self.confFile = confFile
        self.confDir  = Path(__file__).resolve().parents[2]
        self._loadSettings()
        self.host = self.settings.get('gameserver.host', '127.0.0.1')
        self.port = int(self.settings.get('gameserver.port', 5101))
        self.numGames = int(self.settings.get('gameserver.numgames', 1))
        self.db = None
        self.debug = asbool(self.settings.get('autobahn.debug'))

    def run(self):
        self.setupLogging()
        self.setupFactories()
        self.setupGames()
        self.start()

    def _loadSettings(self):
        # Our Paste settings are shared with the Game-Coordinator
        self.settings = {}
        cfg = appconfig("config:"+self.confFile,
                        relative_to=str(self.confDir))
        while cfg:
            self.settings.update(cfg)
            ctx = getattr(cfg.context, "next_context", None)
            cfg = ctx.config() if ctx else None
        self.settings['session.secret'] = SessionKey.secret
        if asbool(self.settings.get('asyncio.debug')):
            os.environ['PYTHONASYNCIODEBUG'] = '1'

    def setupLogging(self):
        loggersConf = self.settings.get('loggersConfig', self.confFile)
        confPath = str(self.confDir/loggersConf)
        fileConfig(confPath,
                   {'__file__': confPath, 'here': str(self.confDir)},
                   disable_existing_loggers=False)

        log = logging.getLogger(__name__)
        log.info("************ GameServer logging started ************")
        log.info("host        = %s", self.host)
        log.info("port        = %s", self.port)
        log.info("confDir     = %s", str(self.confDir))
        log.info("confFile    = %s", self.confFile)
        log.info("loggersConf = %s", loggersConf)

    def setupFactories(self):
        # setup WAMP factories
        log = logging.getLogger(__name__)
        log.debug("setupFactories")
        routerFactory  = RouterFactory(debug=self.debug)
        self.sessionFactory = RouterSessionFactory(routerFactory)
        self.sessionFactory.session = DominoesRouterSession

        self.transportFactory = WampWebSocketServerFactory(self.sessionFactory,
                                                          debug_wamp=self.debug)
        self.transportFactory.app      = self
        self.transportFactory.protocol = DominoesProtocol
        self.transportFactory.setProtocolOptions(failByDrop = False)

    def setupGames(self):
        log = logging.getLogger(__name__)
        log.debug("setupGames")
        gameSessionFactory = GameSessionFactory(self)
        for gameId in range(1, self.numGames+1):
            self.sessionFactory.add(gameSessionFactory(gameId))

    @asyncio.coroutine
    def setupDB(self):
        log = logging.getLogger(__name__)
        log.debug("setupDB")
        url = make_url(self.settings['sqlalchemy.url'])
        self.db = yield from create_engine(database=url.database,
                                           user=url.username,
                                           password=url.password,
                                           host=url.host,
                                           port=url.port)

    def start(self):
        # start the server
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.setupDB())
        coro = loop.create_server(self.transportFactory, self.host, self.port)
        server = loop.run_until_complete(coro)
        #loop.run_until_complete(blather())

        try:
            # now enter the asyncio event loop
            loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.close()
            loop.close()

@asyncio.coroutine
def blather():
    while True:
        print ("hello")
        yield from asyncio.sleep(5)

def main():
    # based on pyramid.scripts.pserve.PServeCommand
    parser = ArgumentParser(description="Run the DavezDominoes GameServer "
                                        "(WAMP Router+Application)")
    parser.add_argument("conf_file", metavar="conf-file",
                        help="What config file to use (e.g. dev.ini)")
    parser.add_argument("command", nargs='?',
                        choices=["start", "stop", "restart", "status"],
                        help="Start/stop/restart in daemon mode")
    parser.add_argument("--daemon",
                        action="store_const", dest="command", const="start",
                        help="Run in daemon (background) mode")
    parser.add_argument("--stop-daemon",
                        action="store_const", dest="command", const="stop",
                        help="Stop a daemonized server")
    parser.add_argument("--status",
                        action="store_const", dest="command", const="status",
                        help="Show the status of the server")
    parser.add_argument("--pid-file", default="gameserver.pid",
                        help="Save PID to file, when daemonized")
    parser.add_argument("--log-file",
                        help="Redirect stdout & stderr to log file")
    # TODO
    #parser.add_argument("--user",  help="Set the user, when daemonized")
    #parser.add_argument("--group", help="Set the group, when daemonized")

    args = parser.parse_args()

    if args.command in ("stop", "restart"):
        daemon = DaemonHandle(args.pid_file, parser.prog)
        if daemon.pid:
            retval = daemon.stop()
            if retval == 0:
                print("Stopped GameServer PID {}".format(daemon.pid))
            else:
                print("Failed to stop GameServer PID {}".format(daemon.pid))
                return retval
        else:
            print("GameServer is already stopped")

    if args.command in ("start", "restart"):
        daemon = DaemonHandle(args.pid_file, parser.prog)
        if daemon.pid:
            # Check this up front, so we don't load the app config unnecessarily
            print("Daemon is already running (PID: {} from file {})"
                  .format(daemon.pid, daemon.filename))
            return 1
        # OK let's try and start up the app now
        logFile = args.log_file
        if not logFile:
            logFile = "gameserver.log"
        app = DominoesApp(args.conf_file)
        retval = daemon.start(app.run, log=logFile)
        # TODO , user=args.user, group=args.group)
        if retval == 0:
            print("Started GameServer PID {}".format(daemon.pid))
        else:
            print("Failed to start GameServer")
            return retval

    elif args.command == "status":
        daemon = DaemonHandle(args.pid_file, parser.prog)
        if daemon.pid:
            print("GameServer running with PID {}".format(daemon.pid))
        else:
            print("GameServer is stopped")
            return 1

    elif args.command == None:
        if args.log_file:
            # FIXME I don't really see the need for LazyWriter
            sys.stdout = sys.stderr = LazyWriter(args.log_file, 'a')
        app = DominoesApp(args.conf_file)
        app.run()

    return 0

if __name__ == '__main__':
    main()
