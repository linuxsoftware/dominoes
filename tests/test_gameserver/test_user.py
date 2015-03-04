#---------------------------------------------------------------------------
# User model tests
#---------------------------------------------------------------------------

from ..testcase import TestCase
from .helpers import asynctest, UnitTestCase
import asyncio
from flexmock import flexmock
from davezdominoes.gameserver.dbuser import DbUser
from davezdominoes.gameserver.oauthuser import GoogleUser
from davezdominoes.gameserver.oauthuser import FacebookUser
from davezdominoes.gameserver.oauthuser import GitHubUser

#---------------------------------------------------------------------------
class DbUserTests(TestCase):
    def test_init(self):
        row = flexmock(id        = 13,
                       login     = "bernard",
                       name      = "Bernard Black",
                       email     = "bernard.black@blackbooks.co.uk",
                       gauth_key = "0102030405060708090a")
        user = DbUser(row)
        self.assertNotEqual(user.login, "tolstoy")
        self.assertEqual(user.login, "bernard")
        self.assertEqual(user.name, "Bernard Black")
        self.assertNotEqual(user.email, "")
        self.assertEqual(user.usesGauth, True)
        self.assertEqual(user.loginMethod, "database")
        self.assertEqual(user.avatarUrl,
                         "//gravatar.com/avatar/"
                         "2b71e0d6c5e13257fcfe82834ac5176d?d=wavatar&s=16")

#---------------------------------------------------------------------------
class GoogleUserTests(TestCase):
    def test_init(self):
        info = {'id':         "1019",
                'name':       "Nick Voleur",
                'picture':    "https://lh6.googleusercontent.com/-Vv8KjmVw6rA/"
                              "AAAAAAAAAAI/AAAAAAAAAAA/BnY0iCeyyHQ/photo.jpg"}
        token = {'access_token': "HocusPocusbEscu"}
        user = GoogleUser(info, token)
        self.assertEqual(user.login, "google:1019")
        self.assertEqual(user.name, "Nick Voleur")
        self.assertEqual(user.loginMethod, "google-oauth")
        self.assertEqual(user.token, token)
        self.assertEqual(user.avatarUrl,
                         "https://lh6.googleusercontent.com/-Vv8KjmVw6rA/"
                         "AAAAAAAAAAI/AAAAAAAAAAA/BnY0iCeyyHQ/photo.jpg?sz=16")

#---------------------------------------------------------------------------
class FacebookUserTests(TestCase):
    def test_init(self):
        info = {'id': "123", 'name': "Enid Katzenjammer"}
        token = {'access_token': "Qszo!XzsoTintullum"}
        user = FacebookUser(info, token)
        self.assertEqual(user.login, "facebook:123")
        self.assertEqual(user.name, "Enid Katzenjammer")
        self.assertEqual(user.loginMethod, "facebook-oauth")
        self.assertEqual(user.token, token)
        self.assertEqual(user.avatarUrl,
                         "https://graph.facebook.com/123/picture?"
                         "width=16&height=16")

#---------------------------------------------------------------------------
class GitHubUserTests(TestCase):
    def test_init(self):
        info = {'login':      "surfking",
                'name':       "Manny Bianco",
                'avatar_url': "https://avatars2.githubusercontent.com"
                              "/u/344?v=3"}
        token = {'access_token': "Xyzzyplugh"}
        user = GitHubUser(info, token)
        self.assertEqual(user.login, "github:surfking")
        self.assertEqual(user.name, "Manny Bianco")
        self.assertEqual(user.loginMethod, "github-oauth")
        self.assertEqual(user.avatarUrl,
                         "https://avatars2.githubusercontent.com"
                         "/u/344?v=3&s=16")

#---------------------------------------------------------------------------
class MoreUserTests(TestCase):
    """Generic user tests"""
    def test_comparison(self):
        user1 = DbUser(flexmock(id        = 1965,
                                login     = "jack",
                                name      = "Jack Parker",
                                email     = "79461.62@compuserve.com",
                                gauth_key = None))
        user2 = DbUser(flexmock(id        = 1966,
                                login     = "jack",
                                name      = "Jack Parker",
                                email     = "jparker@aol.com",
                                gauth_key = None))
        user3 = FacebookUser({'id': "1973", 'name': "Sam Robinson"}, "")
        self.assertIsNot(user1, user2)
        self.assertEqual(user1, user2)
        self.assertNotEqual(user1, user3)

#---------------------------------------------------------------------------
#---------------------------------------------------------------------------
