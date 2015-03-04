#---------------------------------------------------------------------------
# Testing infrastructure
#---------------------------------------------------------------------------
import unittest
from os import path
from pyramid import testing
from pyramid.paster import get_appsettings
from webob.multidict import MultiDict
from webtest import TestApp
import logging
from .. testcase import TestCase
import davezdominoes.gamecoordinator
import davezdominoes.gamecoordinator.routes
import davezdominoes.gamecoordinator.webassets
from davezdominoes.gamecoordinator.models.meta import DBSession

def neverCommit(request, response):
    return True

class DummyRequest(testing.DummyRequest):
    def __init__(self):
        testing.DummyRequest.__init__(self)
        self.POST = MultiDict(self.POST)
        self.GET  = MultiDict(self.GET)
        self.user = None

class UnitTestCase(TestCase):
    """Base test case for pyramid unittests."""
    def setUp(self):
        self.config = testing.setUp()
        davezdominoes.gamecoordinator.routes.includeme(self.config)
#        davezdominoes.gamecoordinator.webassets.includeme(self.config)

    def tearDown(self):
        testing.tearDown()


class FuncTestCase(TestCase):
    def setUp(self):
        here =  path.abspath(path.dirname(__file__))
        settings = get_appsettings(path.join(here, 'tests.ini'))
        app = davezdominoes.gamecoordinator.main({}, **settings)
        self.testapp = TestApp(app)

    def tearDown(self):
        DBSession.remove()
        del self.testapp
        for handler in logging.getLogger("").handlers:
            handler.flush()
            handler.close()

