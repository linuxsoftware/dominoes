from pyramid.view import view_config
from ..models import GameServer
from ..models import Game


@view_config(route_name='games',
             renderer='games.mako',
             permission='view')
def viewGames(request):
    games  = Game.getAll()
    info = {'games': games}
    return info


@view_config(route_name='game',
             renderer='game.mako',
             permission='play')
def viewGame(request):
    gameId = request.matchdict['id']
    #TODO check if this is a valid id
    return {'gameId': gameId}



