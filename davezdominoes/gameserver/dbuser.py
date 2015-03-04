# ------------------------------------------------------------------------------
# Database User Resources
# ------------------------------------------------------------------------------

import sys
import asyncio
from hashlib import md5
from sqlalchemy.sql import and_
from ..gamecoordinator.models import User as UserModel
from ..commoncode.utils import addUrlQueryParams
from .user import User

import logging
log = logging.getLogger(__name__)


# ------------------------------------------------------------------------------
# Database User
# ------------------------------------------------------------------------------
class DbUser(User):
    loginMethod = "database"

    def __init__(self, row):
        self.id        = row.id
        self.login     = row.login
        self.name      = row.name
        self.email     = row.email
        self.usesGauth = row.gauth_key not in ("", None)

    def getAvatarUrl(self, size=None):
        hash = md5(self.email.encode('utf-8')).hexdigest()
        url = "//gravatar.com/avatar/{}?d=wavatar".format(hash)
        if size:
            url = addUrlQueryParams(url, s=size)
        return url

# ------------------------------------------------------------------------------
# UserFactory Worker
# ------------------------------------------------------------------------------
@asyncio.coroutine
def getDbUser(session):
    table = UserModel.__table__
    with (yield from session.app.db) as conn:
        qry = table.select().where(and_(table.c.login == session.login,
                                        table.c.is_active == True))
        res = yield from conn.execute(qry)
        row = yield from res.fetchone()
    if row:
        user = DbUser(row)
        user.gauthVerified = session.get("userVerified", False)
        if user.gauthVerified or not user.usesGauth:
            return user

dbWorkers = {DbUser.loginMethod: getDbUser}

# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
