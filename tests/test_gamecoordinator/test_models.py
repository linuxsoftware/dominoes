#---------------------------------------------------------------------------
# Model tests
#---------------------------------------------------------------------------

from .helpers import UnitTestCase
from pyramid.testing import DummyResource
from davezdominoes.gamecoordinator.models import User

#---------------------------------------------------------------------------
class UserTests(UnitTestCase):
    def test_initUser(self):
        user = User()
        user.login = "bernard"
        user.name  = "Bernard Black"
        user.email = "bernard.black@blackbooks.co.uk"
        self.assertNotEqual(user.login, "tolstoy")
        self.assertEqual(user.login, "bernard")
        self.assertEqual(user.name, "Bernard Black")
        self.assertNotEqual(user.email_confirm, "")
        self.assertEqual(user.failed_logins, 0)
        self.assertFalse(user.is_active)
        self.assertEqual(user.avatarUrl,
                         "//gravatar.com/avatar/"
                         "2b71e0d6c5e13257fcfe82834ac5176d?s=50&d=wavatar")

    def test_password(self):
        user = User()
        user.password = "not telling"
        self.assertNoAttr(user, "password")
        self.assertFalse(user.verifyPassword("don't know"))
        self.assertTrue(user.verifyPassword("not telling"))

#---------------------------------------------------------------------------
