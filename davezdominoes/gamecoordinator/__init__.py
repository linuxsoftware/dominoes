# ------------------------------------------------------------------------------
#  Davez Dominoes!
# ------------------------------------------------------------------------------

from pyramid.config import Configurator
from pyramid.paster import setup_logging
from pyramid.events import ApplicationCreated, subscriber
from sqlalchemy import engine_from_config
from .models.meta import DBSession, Base
from .models.user import User
from .models.oauthuser import getOauthUser
from .utils import getSetupInfo, secureSettings, getGitTag
from datetime import datetime
from pprint import pformat
import atexit
import sys
from contextlib import suppress
from sqlalchemy.exc import ProgrammingError
from secret import SessionKey

import logging
log = logging.getLogger(__name__)


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    settings['here']     = global_config.get('here', '.')
    settings['__file__'] = global_config.get('__file__', 'dev.ini')
    settings['session.secret'] = SessionKey.secret
    loggersConfig = settings.get('loggersConfig')
    logging.captureWarnings(True)
    if loggersConfig:
        setup_logging(loggersConfig)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    settings['setup']  = getSetupInfo('davezdominoes')
    settings['revtag'] = getGitTag()
    config = Configurator(settings=settings)
    config.include('pyramid_webassets') # moving this to .ini breaks tests
    config.include('.renderers')
    config.include('.routes')
    config.include('.security')
    config.include('.webassets')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_request_method(getUser, 'user', reify=True)
    config.add_request_method(verifyUser)
    config.add_request_method(unverifyUser)
    config.add_request_method(getRevision, 'revision', reify=True)
    config.add_request_method(getRevStr, 'revstr', reify=True)
    config.add_request_method(getUserTimeOut, 'userTimeOut', reify=True)
    config.scan()
    log.warning("Game-Coordinator starting work at {}".format(datetime.now().isoformat(' ')))
    atexit.register(goodbye)
    return config.make_wsgi_app()

def goodbye():
    if log:
        log.info("Shutting down at {}".format(datetime.now().isoformat(' ')))
    if logging:
        for handler in logging.getLogger("").handlers:
            handler.flush()
            handler.close()

# ------------------------------------------------------------------------------
# Current User functions
# from http://docs.pylonsproject.org/projects/pyramid_cookbook/en/latest/auth/user_object.html
# ------------------------------------------------------------------------------
def getUser(request):
    user = None
    login = request.unauthenticated_userid
    if login:
        loginMethod = request.session.get('loginMethod', "")
        if loginMethod.endswith("-oauth"):
            token = request.session.get('oauthToken')
            user = getOauthUser(loginMethod, login, token)
            if user:
                request.session['oauthToken'] = user.token
        else: # database
            #log.debug("Looking up user %s " % login)
            user = User.getByLogin(login)
            if user:
                user.gauthVerified = request.session.get("userVerified", False)
    return user

def verifyUser(request):
    user = request.user
    if user:
        user.gauthVerified = request.session["userVerified"] = True

def unverifyUser(request):
    request.session["userVerified"] = False
    user = request.user
    if user:
        user.gauthVerified = False

# ------------------------------------------------------------------------------
# For added convenience
# ------------------------------------------------------------------------------
def getRevision(request):
    revTag = request.registry.settings.revtag
    if revTag:
        return {'rev': revTag}

def getRevStr(request):
    revTag = request.registry.settings.revtag
    if revTag:
      return "rev={}".format(request.registry.settings.revtag)

def getUserTimeOut(request):
    retval = 300
    timeOutSetting = None#GlobalSetting.getById('usertimeout')
    if timeOutSetting:
        with suppress(TypeError, ValueError):
            retval = int(timeOutSetting.value)
    return retval
