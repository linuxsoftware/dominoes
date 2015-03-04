# ------------------------------------------------------------------------------
# All the routes are defined in this module
# ------------------------------------------------------------------------------
from .security import UserSettings
from .models   import UserBureau    # for the class of user to use

import logging
log = logging.getLogger(__name__)

def includeme(config):
    """Set up the routes"""
    # Login pages
    config.add_route('login',             '/login')
    config.add_route('forgotpwd',         '/resetpwd')
    config.add_route('pwdemailsent',      '/pwdemailsent')
    config.add_route('resetpwd',          '/resetpwd/{token}')
    config.add_route('logout',            '/logout')
    config.add_route('altlogin',          '/login/{method}',
                     factory=UserBureau,  traverse='/{method}')
    config.add_route('altconnect',        '/connect/{method}',
                     factory=UserBureau,  traverse='/{method}')

    # User pages
    config.add_route('register',          '/user/register')
    config.add_route('registered',        '/user/registered')
    config.add_route('activate',          '/user/activate/{token}')
    config.add_route('user',              '/user',
                     factory=UserSettings)
    config.add_route('changepwd',         '/user/changepwd',
                     factory=UserSettings)
    config.add_route('setgauth',          '/user/setgauth',
                     factory=UserSettings)
    config.add_route('gauth.png',         '/user/gauth.png',
                     factory=UserSettings)

    # Game pages
    config.add_route('games',             '/')
    config.add_route('game',              '/game{id}')
    # TODO GameMill

    # XHR JSON data

    log.info("routes added")

