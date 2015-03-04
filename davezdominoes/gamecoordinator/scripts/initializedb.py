#---------------------------------------------------------------------------
# Initialize the database
#---------------------------------------------------------------------------
import os
import sys
import transaction
from decimal import Decimal
from datetime import datetime

from sqlalchemy import engine_from_config

from pyramid.paster import get_appsettings
from pyramid.paster import setup_logging
from ..models.meta import Base

from pyramid.scripts.common import parse_vars

from ..models import (
    DBSession,
    GameServer,
    Game,
    User,
    )


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s dev.ini")' % (cmd, cmd))
    sys.exit(1)

def setupAdmin(config_uri):
    instance = config_uri[:3].upper()
    admin = User("admin")
    admin.name        = "Admin User"
    admin.password    = "boneyard"
    admin.email       = "dominoes+{}+admin@software.net.nz".format(instance)
    admin.is_active   = True
    admin.insert(True)

def setupHarry(config_uri):
    admin = User("harry")
    admin.name        = "Harry Stone"
    admin.password    = "nightcourt"
    admin.email       = "harry.the.hat@software.net.nz"
    admin.is_active   = True
    admin.insert(True)

def setupGameServers():
    for srvrId in range(1, 2):
        gsrv = GameServer(srvrId)
        gsrv.insert()

def main(argv=sys.argv):
    if len(argv) < 2:
        usage(argv)
    config_uri = argv[1]
    options = parse_vars(argv[2:])
    setup_logging(config_uri)
    settings = get_appsettings(config_uri, options=options)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with transaction.manager:
        setupAdmin(config_uri)
        setupHarry(config_uri)
        setupGameServers()
