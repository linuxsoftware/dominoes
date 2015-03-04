#---------------------------------------------------------------------------
# Functional tests
# These use the real app, but with a test profile
#---------------------------------------------------------------------------

from .helpers import FuncTestCase
from pyramid.testing import DummyResource


#---------------------------------------------------------------------------
class BasicFuncTests(FuncTestCase):
    def test_pageNotFound(self):
        res = self.testapp.get('/SomePage', status=404)
        self.assertIn(b'Not Found', res.body)

    def test_pageFound(self):
        res = self.testapp.get('/user/register', status=200)

#---------------------------------------------------------------------------
class LoginFuncTests(FuncTestCase):
    def test_successfulLogin(self):
        res = self.testapp.get("/login", status=200)
        self.assertIn(b'Login', res.body)
        form = res.form
        form['login']    =  "harry"
        form['password'] =  "nightcourt"
        res = form.submit('loginBtn', status=302)

    def test_failedLogin(self):
        res = self.testapp.get("/login", status=200)
        self.assertIn(b'Login', res.body)
        form = res.form
        form['login']    =  "harry"
        form['password'] =  "inkorrekt"
        res = form.submit('loginBtn', status=200)
        self.assertIn(b'Login', res.body)

    def test_logoutLinkWhenLoggedIn(self):
        res = self.testapp.get("/login", status=200)
        form = res.form
        form['login']    =  "harry"
        form['password'] =  "nightcourt"
        form.submit('loginBtn', status=302)
        res = self.testapp.get("/user", status=200)
        self.assertIn(b'Logout', res.body)

    def test_noLogoutLinkAfterLoggedOut(self):
        res = self.testapp.get("/login", status=200)
        form = res.form
        form['login']    =  "harry"
        form['password'] =  "nightcourt"
        form.submit('loginBtn', status=302)
        res = self.testapp.get("/logout", status=302)
        self.assertNotIn(b'Logout', res.body)

#---------------------------------------------------------------------------
