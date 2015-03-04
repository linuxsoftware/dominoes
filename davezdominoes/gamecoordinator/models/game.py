# ------------------------------------------------------------------------------
# Game Resources
# ------------------------------------------------------------------------------
from sqlalchemy import (Table,
                        Column,
                        ForeignKey,
                        Boolean,
                        Integer,
                        String,
                        Text)
from sqlalchemy.orm import relationship
from .meta import Base, IntegerDefaults
from enum import Enum
from contextlib import suppress


import logging
log = logging.getLogger(__name__)


class GameServer(Base):
    __tablename__ = 'game_server'
    id                 = Column(Integer, primary_key=True)
    pid                = Column(Integer, **IntegerDefaults)
    current_game       = relationship("Game", uselist=False, backref="server")

    def __init__(self, srvrId=None):
        self.id           = srvrId
        self.current_game = Game("New Game")

    @property
    def url(self):
        return "/ws/game{}".format(self.id)


class Game(Base):
    """Game"""
    __tablename__ = 'game'
    id                 = Column(Integer, primary_key=True)
    game_server_id     = Column(Integer, ForeignKey('game_server.id'))
    description        = Column(Text)
    has_started        = Column(Boolean)
    is_public          = Column(Boolean)
    players            = relationship("User", secondary="game_player",
                                      backref="games")
    winning_user_id    = Column(Integer, ForeignKey('user.id'))
    winner             = relationship("User", foreign_keys=winning_user_id)

    def __init__(self, description):
        self.description = description
        self.has_started = False
        self.is_public   = False

    @property
    def name(self):
      return "Game #{}".format(self.game_server_id)

    @property
    def url(self):
        return "/game{}".format(self.game_server_id)

    @property
    def status(self):
        if not self.players:
            return Game.Status.Empty
        elif len(self.players) <= 1: #TODO GameRules.minNumPlayers
            return Game.Status.Waiting
        elif not self.has_started:
            return Game.Status.Ready
        elif not self.winner:
            return Game.Status.Started
        else:
            return Game.Status.Finished

    def addPlayer(self, player):
        if player not in self.players:
            self.players.append(player)

    def removePlayer(self, player):
        with suppress(ValueError):
            self.players.remove(player)

class GameMill():
    pass

# join Users to Games
companylinkprod = Table('game_player', Base.metadata,
    Column('game_id', Integer, ForeignKey('game.id', ondelete='cascade'),
           primary_key=True),
    Column('user_id', Integer, ForeignKey('user.id', ondelete='cascade'),
           primary_key=True)
)


