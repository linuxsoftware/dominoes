# ------------------------------------------------------------------------------
# Alternative Login User Resources
# ------------------------------------------------------------------------------
import os
import inspect
import time
from pyramid.security import Allow
from secret import GoogleCredentials, FacebookCredentials, GitHubCredentials
from ...commoncode.utils import addUrlQueryParams
# TODO use bare oauthlib?
from requests_oauthlib import OAuth2Session
from requests_oauthlib.compliance_fixes import facebook_compliance_fix
import requests

from oauthlib.common import urldecode
from oauthlib.oauth2 import WebApplicationClient


# XXX For debugging with WingIDE
##### import wingdbstub

import logging
log = logging.getLogger(__name__)


def getOauthUser(loginMethod, login, token):
    Cls = UserBureau().get(loginMethod)
    if Cls:
        user = Cls(token)
        if user.login == login:
            return user

class UserBureau:
    def __init__(self, request=None):
        pass

    def __getitem__(self, loginMethod):
        Cls = self.get(loginMethod)
        if Cls is None:
            raise KeyError(loginMethod)
        return Cls

    def get(self, loginMethod, default=None):
        for Cls in list(globals().values()):
            clsLoginMethod = getattr(Cls, 'loginMethod', None)
            # TODO consider using zope interfaces?
            if inspect.isclass(Cls) and loginMethod == clsLoginMethod:
                return Cls
        return default

# FIXME should run on https
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# ------------------------------------------------------------------------------
# Oauth User,  c.f. user.User
# ------------------------------------------------------------------------------
class OauthUser:
    gauthVerified = False
    usesGauth     = False
    loginMethod   = None
    callbackHost  = "http://dominoes.software.net.nz"
    # TODO use https://dominoes....

    def __init__(self, name=''):
        self.login          = name.lower().replace(' ', '')
        self.name           = name
        self.picture        = ""
        self.token          = None

    def __str__(self):
        return "{0.login} ({0.name})".format(self)

    @property
    def __acl__(self):
        return []

    #@property
    #def groups(self):
    #    return [ "login-with:google", "player" ]

    @property
    def avatarUrl(self):
        return self.getAvatarUrl(50)

    def logout(self):
        raise NotImplementedError()

# ------------------------------------------------------------------------------
# Google Oauth, https://developers.google.com/accounts/docs/OAuth2
# ------------------------------------------------------------------------------
class GoogleUser(OauthUser, GoogleCredentials):
    loginMethod  = "google-oauth"
    authzBaseUrl = "https://accounts.google.com/o/oauth2/auth"
    callbackUrl  = "{}/connect/{}".format(OauthUser.callbackHost, loginMethod)
    tokenUrl     = "https://accounts.google.com/o/oauth2/token"
    resourceUrl  = "https://www.googleapis.com/oauth2/v1/userinfo"
    #TODO use https://www.googleapis.com/plus/v1/people/me instead?

    @classmethod
    def authzUrl(cls, csrfToken):
        session = OAuth2Session(cls.clientId, scope=["profile"], 
                                redirect_uri=cls.callbackUrl)
        authzUrl, _ = session.authorization_url(cls.authzBaseUrl, csrfToken,
                                                access_type="offline")
        return authzUrl

    @classmethod
    def getUser(cls, code):
        session = OAuth2Session(cls.clientId, redirect_uri=cls.callbackUrl)
        token = session.fetch_token(cls.tokenUrl, code,
                                    client_secret=cls.clientSecret)
        return cls(token)

    def __init__(self, oauthToken):
        super().__init__()
        # XXX FOR TESTING ONLY
        # XXX oauthToken['expires_at'] = time.time() - 10
        tokenExpiresAt = float(oauthToken.get('expires_at', 0))
        tokenExpiresIn = int(tokenExpiresAt - time.time())
        oauthToken['expires_in'] = tokenExpiresIn
        tokenType = oauthToken.get('token_type')
        log.debug("Token expires in {tokenExpiresIn}, token_type {tokenType} "
                  .format(**locals()))
        self.token = oauthToken
        def setOauthToken(oauthToken): self.token = oauthToken
        refreshParams = {'client_id':     self.clientId,
                         'client_secret': self.clientSecret}
        session = OAuth2Session(self.clientId, token=oauthToken,
                                auto_refresh_url=self.tokenUrl,
                                auto_refresh_kwargs=refreshParams,
                                token_updater=setOauthToken)
        response = session.get(self.resourceUrl)
        userInfo = response.json() if response.ok else {}
        self.name    = userInfo.get('name',    "")
        self.login   = "google:{}".format(userInfo.get('id', ""))
        self.picture = userInfo.get('picture', "")

    def getAvatarUrl(self, size=None):
        url = self.picture
        if size:
            url = addUrlQueryParams(url, sz=size)
        return url

    def logout(self):
        accessToken = None
        if self.token:
            accessToken = self.token.get('access_token')
        if accessToken is None: return
        # requests_oauth doesn't yet support token revocation
        # yet another reason for using bare oauthlib?
        client = WebApplicationClient(self.clientId, self.token)
        revokeUrl = "https://accounts.google.com/o/oauth2/revoke"
        url, headers, body = \
            client.prepare_token_revocation_request(revokeUrl, accessToken)
        response = requests.post(url, headers=headers,
                                 data=dict(urldecode(body)))

# ------------------------------------------------------------------------------
# Facebook, https://developers.facebook.com/docs/facebook-login/v2.2
# ------------------------------------------------------------------------------
class FacebookUser(OauthUser, FacebookCredentials):
    loginMethod  = "facebook-oauth"
    authzBaseUrl = "https://www.facebook.com/dialog/oauth"
    callbackUrl  = "{}/connect/{}".format(OauthUser.callbackHost, loginMethod)
    tokenUrl     = "https://graph.facebook.com/oauth/access_token"
    resourceUrl  = "https://graph.facebook.com/me"

    @classmethod
    def authzUrl(cls, csrfToken):
        session = OAuth2Session(cls.clientId, scope=["public_profile"], 
                                redirect_uri=cls.callbackUrl)
        authzUrl, _ = session.authorization_url(cls.authzBaseUrl, csrfToken)
        return authzUrl

    @classmethod
    def getUser(cls, code):
        session = OAuth2Session(cls.clientId, redirect_uri=cls.callbackUrl)
        session = facebook_compliance_fix(session)
        token = session.fetch_token(cls.tokenUrl, code,
                                    client_secret=cls.clientSecret)
        return cls(token)

    def __init__(self, oauthToken):
        super().__init__()
        tokenExpiresIn = float(oauthToken.get('expires_in', 0))
        tokenType = oauthToken.get('token_type')
        log.debug("Token expires_in {tokenExpiresIn}, token_type {tokenType} "
                  .format(**locals()))
        self.token = oauthToken
        session = OAuth2Session(self.clientId, token=oauthToken)
        response = session.get(self.resourceUrl)
        userInfo = response.json() if response.ok else {}
        self.name    = userInfo.get('name',    "")
        facebookId   = userInfo.get('id',      "")
        self.login   = "facebook:{}".format(facebookId)
        self.picture = "https://graph.facebook.com/{}/picture"\
                       .format(facebookId)

    def getAvatarUrl(self, size=None):
        url = self.picture
        if size:
            url = addUrlQueryParams(url, ('width',size), ('height',size))
        return url

    def logout(self):
        url = "https://graph.facebook.com/me/permissions"
        session = OAuth2Session(self.clientId, token=self.token)
        response = session.delete(url)


# ------------------------------------------------------------------------------
# GitHub, https://developer.github.com/v3/oauth
# ------------------------------------------------------------------------------
class GitHubUser(OauthUser, GitHubCredentials):
    loginMethod  = "github-oauth"
    authzBaseUrl = "https://github.com/login/oauth/authorize"
    callbackUrl  = "{}/connect/{}".format(OauthUser.callbackHost, loginMethod)
    tokenUrl     = "https://github.com/login/oauth/access_token"
    resourceUrl  = "https://api.github.com/user"

    @classmethod
    def authzUrl(cls, csrfToken):
        session = OAuth2Session(cls.clientId, redirect_uri=cls.callbackUrl)
        authzUrl, _ = session.authorization_url(cls.authzBaseUrl, csrfToken)
        return authzUrl

    @classmethod
    def getUser(cls, code):
        session = OAuth2Session(cls.clientId, redirect_uri=cls.callbackUrl)
        token = session.fetch_token(cls.tokenUrl, code,
                                    client_secret=cls.clientSecret)
        return cls(token)

    def __init__(self, oauthToken):
        super().__init__()
        self.token = oauthToken
        if not self.check():
            return
        session = OAuth2Session(self.clientId, token=oauthToken)
        response = session.get(self.resourceUrl)
        userInfo = response.json() if response.ok else {}
        self.name    = userInfo.get('name',       "")
        self.login   = "github:{}".format(userInfo.get('login', ""))
        self.picture = userInfo.get('avatar_url', "")

    def getAvatarUrl(self, size=None):
        url = self.picture
        if size:
            url = addUrlQueryParams(url, s=size)
        return url

    def check(self):
        url = self._getAccessTokenUrl()
        if url is None: return False
        response = requests.get(url, auth=(self.clientId, self.clientSecret))
        return response.status_code == requests.codes.ok

    def logout(self):
        url = self._getAccessTokenUrl()
        if url is None: return
        response = requests.delete(url, auth=(self.clientId, self.clientSecret))

    def _getAccessTokenUrl(self):
        if self.token:
            accessToken = self.token.get('access_token')
            if accessToken:
                return "https://api.github.com/applications/{}/tokens/{}"\
                       .format(self.clientId, accessToken)
