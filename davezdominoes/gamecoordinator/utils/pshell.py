# gamecoordinator/utils/pshell.py
from webtest import TestApp
from .. import models
import inspect

def setup(env):
    env.update((name, cls) for name, cls in
               inspect.getmembers(models, inspect.isclass))
    env['DBSession'] = models.DBSession
    env['request'].host = 'dominoes.software.net.nz'
    env['request'].scheme = 'http'
    env['testapp'] = TestApp(env['app'])
