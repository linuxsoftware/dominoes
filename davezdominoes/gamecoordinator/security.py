# ------------------------------------------------------------------------------
# Security Central
# ------------------------------------------------------------------------------
from .models import User
from pyramid.security import Allow, Everyone, Authenticated, ALL_PERMISSIONS
from pyramid.authentication import SessionAuthenticationPolicy
from pyramid.authorization  import ACLAuthorizationPolicy
from .utils.gauth import getSecret, verifyOneTimePassword

import logging
log = logging.getLogger(__name__)


# ------------------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------------------
def includeme(config):
    """Set up the authentication and authorization policies"""
    authnPolicy = SessionAuthenticationPolicy(callback=getGroups)
    authzPolicy = ACLAuthorizationPolicy()
    config.set_authentication_policy(authnPolicy)
    config.set_authorization_policy(authzPolicy)
    config.set_root_factory(Root)

    # Custom predicates
    config.add_view_predicate("userNeedsVerification",
                              UserNeedsVerificationPredicate)
    log.info("security set up")

# ------------------------------------------------------------------------------
# Authentication
# ------------------------------------------------------------------------------
def getGroups(name, request):
    user = request.user
    if user is None:
        log.info("getGroups called for non-existant user %s" % name)
        return None
    if user.usesGauth and not user.gauthVerified:
        log.debug("getGroups called for non-verified user %s" % name)
        return None
    return getGroupsForUser(user)

def getGroupsForUser(user):
    groups = []
    return groups

class Authentication:
    TO_VERIFY, OK, FAILED, LOCKED_OUT = range(4)

def checkAuthentication(name, givenPass):
    """Check the given login and password matches an active user"""
    result = Authentication.FAILED
    name = name.replace(':', ';')
    user = User.getByLogin(name)
    if user:
        if user.failed_logins < 99:
            if givenPass and user.verifyPassword(givenPass):
                log.info("User %s password OK" % name)
                if user.usesGauth: 
                    user.gauthVerified = False
                    result = Authentication.TO_VERIFY
                else:
                    result = Authentication.OK
                    user.failed_logins = 0
            else:
                log.info("User %s authentication FAILED" % name)
                user.failed_logins += 1
        else:
            log.warning("User %s locked out" % name)
            result = Authentication.LOCKED_OUT
    else:
        log.info("User %s does not exist" % name)

    return result, user

def checkVerification(user, givenOtp):
    """Verify the given one-time-password of users who use gauth"""
    result = Authentication.FAILED
    if user.usesGauth:
        if user.failed_logins < 3:
            secret = getSecret(user.gauth_key, user.id)
            if givenOtp and verifyOneTimePassword(givenOtp, secret):
                log.info("User %s verification OK" % user.login)
                result = Authentication.OK
                user.failed_logins = 0
            else:
                log.info("User %s verification FAILED" % user.login)
                user.failed_logins += 1
        else:
            log.warning("User %s locked out" % user.login)
            result = Authentication.LOCKED_OUT
    else:
        log.error("User %s does not use gauth!!!" % user.login)

    return result


# ------------------------------------------------------------------------------
# View Predicates
# ------------------------------------------------------------------------------
class UserNeedsVerificationPredicate(object):
    def __init__(self, flag, config):
        self.flag = flag

    def text(self):
        if self.flag:
            return "User does need verification"
        else:
            return "User does not need verification"
    phash = text

    def __call__(self, context, request):
        user = request.user
        needsVerification = user and user.usesGauth and not user.gauthVerified
        return self.flag == needsVerification

# ------------------------------------------------------------------------------
# Security Domains
# ------------------------------------------------------------------------------
class Root(dict):
    """The root security domain"""
    __acl__ = [(Allow, Everyone,        ()),
               (Allow, Authenticated,   ('view', 'edit', 'play')),
               (Allow, 'role:admin',     ALL_PERMISSIONS) ]

    def __init__(self, request):
        pass

class UserSettings(object):
    """The security domain for user settings"""
    def __init__(self, request):
        self.request = request

    @property
    def __acl__(self):
        # just delegate acl handling to the current user
        if self.request.user:
            return self.request.user.__acl__



