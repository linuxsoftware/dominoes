# ------------------------------------------------------------------------------
# Oauth User Resources
# ------------------------------------------------------------------------------

import sys
import asyncio
import time
import aiohttp
from base64 import b64encode
from .user import User
from secret import GoogleCredentials, FacebookCredentials, GitHubCredentials
from ..commoncode.utils import addUrlQueryParams

import logging
log = logging.getLogger(__name__)


# ------------------------------------------------------------------------------
# UserFactory Workers
# ------------------------------------------------------------------------------
oauthWorkers = {}

def factorymade(cls):
    def getOauthUser(session):
        token = session.get('oauthToken')
        user = yield from cls.getByToken(token)
        if user and user.token != token:
            session['oauthToken'] = user.token
            yield from session.save()
        return user
    oauthWorkers[cls.loginMethod] = getOauthUser
    return cls

# ------------------------------------------------------------------------------
# Google Oauth, https://developers.google.com/accounts/docs/OAuth2
# ------------------------------------------------------------------------------
@factorymade
class GoogleUser(User, GoogleCredentials):
    loginMethod  = "google-oauth"

    @classmethod
    @asyncio.coroutine
    def getByToken(cls, oauthToken):
        tokenType = oauthToken.get('token_type')
        if tokenType != "Bearer":
            return None

        nowish = time.time()
        if oauthToken.get('expires_at', nowish+10) < nowish:
            # refresh token if it is expired, if unsure don't bother
            oauthToken = yield from cls.refreshToken(oauthToken)
            if oauthToken.get('expires_at', nowish+10) < nowish:
                log.error("Token expired, cannot refresh")
                return None

        accessToken = oauthToken.get('access_token')
        if accessToken is None:
            return None

        url = "https://www.googleapis.com/oauth2/v1/userinfo"
        #TODO use https://www.googleapis.com/plus/v1/people/me instead?
        headers = { 'Authorization': "Bearer {}".format(accessToken) }
        response = yield from aiohttp.request('get', url, headers=headers)
        if response.status == 200:
            userInfo = yield from response.json()
            return cls(userInfo, oauthToken)

    @classmethod
    @asyncio.coroutine
    def refreshToken(cls, oauthToken):
        log.debug("Try and refresh token")
        refreshToken = oauthToken.get('refresh_token')
        if refreshToken is None:
            return oauthToken

        payload = {'client_id':     cls.clientId,
                   'client_secret': cls.clientSecret,
                   'refresh_token': refreshToken,
                   'grant_type':    'refresh_token'}
        url = "https://accounts.google.com/o/oauth2/token"
        response = yield from aiohttp.request('post', url, data=payload)
        if response.status != 200:
            return oauthToken

        refreshment = yield from response.json()
        if refreshment.get('token_type') != "Bearer":
            return oauthToken

        expiresIn = refreshment.get('expires_in', 1)
        if 'expires_at' not in refreshment:
            refreshment['expires_at'] = time.time() + expiresIn
        oauthToken.update(refreshment)
        return oauthToken

    def __init__(self, userInfo, oauthToken):
        self.name    = userInfo.get('name', "")
        self.login   = "google:{}".format(userInfo.get('id', ""))
        self.picture = userInfo.get('picture', "")
        self.token   = oauthToken

    def getAvatarUrl(self, size=None):
        url = self.picture
        if size:
            url = addUrlQueryParams(url, sz=size)
        return url

# ------------------------------------------------------------------------------
# Facebook, https://developers.facebook.com/docs/facebook-login/v2.2
# ------------------------------------------------------------------------------
@factorymade
class FacebookUser(User, FacebookCredentials):
    loginMethod  = "facebook-oauth"

    @classmethod
    @asyncio.coroutine
    def getByToken(cls, oauthToken):
        try:
            payload = {'access_token': oauthToken['access_token']}
        except KeyError:
            return None
        url = "https://graph.facebook.com/me"
        response = yield from aiohttp.request('get', url, params=payload)
        if response.status == 200:
            userInfo = yield from response.json()
            return cls(userInfo, oauthToken)

    def __init__(self, userInfo, oauthToken):
        self.name    = userInfo.get('name', "")
        fbId         = userInfo.get('id', "")
        self.login   = "facebook:{}".format(fbId)
        self.picture = "https://graph.facebook.com/{}/picture".format(fbId)
        self.token   = oauthToken

    def getAvatarUrl(self, size=None):
        url = self.picture
        if size:
            url = addUrlQueryParams(url, ('width', size), ('height', size))
        return url

# ------------------------------------------------------------------------------
# GitHub, https://developer.github.com/v3/oauth
# ------------------------------------------------------------------------------
@factorymade
class GitHubUser(User, GitHubCredentials):
    loginMethod  = "github-oauth"

    @classmethod
    @asyncio.coroutine
    def getByToken(cls, oauthToken):
        accessToken = oauthToken.get('access_token')
        if accessToken is None:
            return None
        if not cls.checkToken(accessToken):
            return None
        url = "https://api.github.com/user"
        headers = { 'Authorization': "token {}".format(accessToken) }
        response = yield from aiohttp.request('get', url, headers=headers)
        if response.status == 200:
            userInfo = yield from response.json()
            return cls(userInfo, oauthToken)

    @classmethod
    @asyncio.coroutine
    def checkToken(cls, accessToken):
        url = "https://api.github.com/applications/{}/tokens/{}"\
              .format(cls.clientId, accessToken)
        auth="{0.clientId}:{0.clientSecret}".format(cls)
        b64auth=b64encode(auth.encode('utf-8'))
        headers= { 'Authorization': "Basic {}".format(b64auth) }
        response = yield from aiohttp.request('get', url, headers=headers)
        return response.status == 200

    def __init__(self, userInfo, oauthToken):
        self.name    = userInfo.get('name', "")
        self.login   = "github:{}".format(userInfo.get('login', ""))
        self.picture = userInfo.get('avatar_url', "")
        self.token   = oauthToken

    def getAvatarUrl(self, size=None):
        url = self.picture
        if size:
            url = addUrlQueryParams(url, s=size)
        return url

# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
