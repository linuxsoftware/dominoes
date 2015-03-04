#---------------------------------------------------------------------------
# View tests 
#---------------------------------------------------------------------------

import sys
from pyramid.testing import DummyResource
from .helpers import UnitTestCase, DummyRequest
import warnings


class ViewGameTests(UnitTestCase):
    # depends on DB ATM
    # def test_viewGames(self):
    #     from davezdominoes.gamecoordinator.views.game import viewGames
    #     request = DummyRequest()
    #     info = viewGames(request)
    #     self.assertIn('games', info)

    def test_viewGame(self):
        from davezdominoes.gamecoordinator.views.game import viewGame
        request = DummyRequest()
        request.matchdict = {'id': "1"}
        info = viewGame(request)
        self.assertIn('gameId', info)

class ViewUserTests(UnitTestCase):
    def setUp(self):
        super().setUp()
        warnings.filterwarnings("ignore",
                                "wtforms.ext.sqlalchemy is deprecated",
                                DeprecationWarning,
                                "wtforms.ext.sqlalchemy")

    def tearDown(self):
        super().tearDown()

    def test_newUser(self):
        from davezdominoes.gamecoordinator.views.user import newUser
        request = DummyRequest()
        info = newUser(request)
        self.assertIn('btns', info)
        btns = info['btns']
        self.assertHasAttr(btns, 'okBtn')
        self.assertIn('form', info)
        form = info['form']
        self.assertHasAttr(form, 'login')
        self.assertHasAttr(form, 'name')
        self.assertHasAttr(form, 'email')
        self.assertHasAttr(form, 'password')
        self.assertEqual(form.name.data, "")

    def test_registered(self):
        from davezdominoes.gamecoordinator.views.user import registered
        request = DummyRequest()
        info = registered(request)
        self.assertIn('btns', info)
        btns = info['btns']
        self.assertHasAttr(btns, 'okBtn')

    # depends on DB
    # def test_activate(self):
    #     from davezdominoes.gamecoordinator.views.user import activate
    #     request = DummyRequest()
    #     request.matchdict = {'token': "12345"}
    #     info = activate(request)
    #     self.assertIn('btns', info)
    #     btns = info['btns']
    #     self.assertHasAttr(btns, 'okBtn')
    #     self.assertTrue(btns.okBtn.disabled)

    def test_editUser(self):
        from davezdominoes.gamecoordinator.views.user import editUser
        request = DummyRequest()
        request.user = DummyResource(name = "Ichabod Bartram")
        info = editUser(request)
        self.assertIn('btns', info)
        btns = info['btns']
        self.assertHasAttr(btns, 'modBtn')
        self.assertEqual(btns.modBtn.label.text, "Change Password")
        self.assertIn('form', info)
        form = info['form']
        self.assertEqual(form.name.data, "Ichabod Bartram")

    def test_changePwd(self):
        from davezdominoes.gamecoordinator.views.user import changePwd
        request = DummyRequest()
        info = changePwd(request)
        self.assertIn('form', info)
        form = info['form']
        self.assertHasAttr(form, 'oldPassword')
        self.assertHasAttr(form, 'password')
        self.assertHasAttr(form, 'password2')

