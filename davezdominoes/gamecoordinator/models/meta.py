# ------------------------------------------------------------------------------
# Meta model module
# ------------------------------------------------------------------------------

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.orm.exc import ObjectDeletedError
from sqlalchemy import inspect
from zope.sqlalchemy import ZopeTransactionExtension
from decimal import Decimal

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))

class Base(object):
    # DBSession convenience functions
    @classmethod
    def getById(cls, id):
        try:
            return DBSession.query(cls).get(id)
        except ObjectDeletedError:
            return None

    @classmethod
    def getAll(cls):
        return DBSession.query(cls).all()
    getList=getAll

    @classmethod
    def getDict(cls):
        key = inspect(cls).primary_key[0].name # probably 'id'
        return dict((getattr(rec, key), rec) for rec in DBSession.query(cls))

    def insert(self, withFlush=False):
        DBSession.add(self)
        if withFlush:
            DBSession.flush()

    def delete(self, withFlush=False):
        DBSession.delete(self)
        if withFlush:
            DBSession.flush()

Base = declarative_base(cls=Base)

IntegerDefaults = {'nullable': False, 'default':  0}
StringDefaults  = {'nullable': False, 'default':  ''}
DecimalDefaults = {'nullable': False, 'default':  Decimal('0.00')}
