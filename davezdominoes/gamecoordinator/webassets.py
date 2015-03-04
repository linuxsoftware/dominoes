# ------------------------------------------------------------------------------
# Web Assets
# ------------------------------------------------------------------------------
#from webassets import Bundle
#from .utils.webassetextns import noop
from .utils.webassetextns import GzipBundle

import logging
log = logging.getLogger(__name__)

def includeme(config):
    """Add WebAsset bundles"""
    stylesheet = GzipBundle("main.css", "login.css", "misc.css", "game.css",
                            filters="cleancss",
                            output="css/dominoes.css")
    config.add_webasset('stylesheet', stylesheet)

    gameClient = GzipBundle("utils.coffee", "dominoes.coffee",
                            "game.coffee", "area.coffee", "bone.coffee",
                            filters="coffeescript,uglifyjs",
                            output="js/dominoes_game.js")
    config.add_webasset('game_client', gameClient)

    adminClient = GzipBundle("utils.coffee", "dominoes.coffee",
                             "admin.coffee",
                             filters="coffeescript,uglifyjs",
                             output="js/dominoes_admin.js")
    config.add_webasset('admin_client', adminClient)

    log.info("webasset bundles added")



