# ------------------------------------------------------------------------------
# User Resources
# ------------------------------------------------------------------------------
from datetime import datetime
from hashlib import md5
from sqlalchemy import (Column,
                        ForeignKey,
                        Integer,
                        String,
                        DateTime,
                        Boolean)
from sqlalchemy.orm import relationship
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from pyramid.security import Allow
from shortuuid import ShortUUID
from passlib.context import CryptContext
from .meta import Base, DBSession, StringDefaults, IntegerDefaults
from passlib.utils import generate_password

import logging
log = logging.getLogger(__name__)


class User(Base):
    __tablename__ = 'user'
    id                 = Column(Integer, primary_key=True) 
    login              = Column(String(20),  unique=True, **StringDefaults)
    name               = Column(String(80), **StringDefaults)
    email              = Column(String(100), unique=True, **StringDefaults)
    email_confirm      = Column(String(40),  unique=True, **StringDefaults)
    pwd                = Column(String(300), nullable=False)
    gauth_key          = Column(String(50))
    failed_logins      = Column(Integer, **IntegerDefaults)
    is_active          = Column(Boolean)
    gauthVerified      = False
    loginMethod        = "database"

    @classmethod
    def getByLogin(cls, login):
        try:
            return DBSession.query(cls).\
                    filter_by(login = login).\
                    filter_by(is_active  = True).\
                    one()
        except (NoResultFound, MultipleResultsFound):
            return None

    @classmethod
    def getByEmailConfirmation(cls, emailConfirmation):
        try:
            return DBSession.query(cls).\
                    filter_by(email_confirm = emailConfirmation).\
                    one()
        except (NoResultFound, MultipleResultsFound):
            return None

    @classmethod
    def getByEmail(cls, email):
        try:
            return DBSession.query(cls).\
                    filter_by(email     = email).\
                    filter_by(is_active  = True).\
                    one()
        except (NoResultFound, MultipleResultsFound):
            return None

    @classmethod
    def getAllActive(cls):
        query = DBSession.query(cls).filter_by(is_active = True)\
                                    .order_by(cls.name)
        return query.all()

    def __init__(self, name=''):
        Base.__init__(self)
        self.login          = name.lower()
        self.name           = name
        self.email          = ""
        self.email_confirm  = ShortUUID().uuid()
        self.password       = generate_password(40)
        self.failed_logins  = 0
        self.is_active      = False

    def __str__(self):
        name = "{0.login} ({0.name})".format(self)
        if self.is_active:
            return name
        else:
            return "~{}".format(name)

    @property
    def __acl__(self):
        return [ (Allow, self.login,         ('view','edit')),
                 (Allow, "role:admin",        'edit'), ]

    #@property
    #def groups(self):
    #    return [ "login-with:database", "player" ]

    PassContext = CryptContext(schemes=["sha512_crypt"])
    def _setPassword(self, password):
        self.pwd  = User.PassContext.encrypt(password)
    password = property(None, _setPassword)

    def verifyPassword(self, givenPass):
        try:
            return User.PassContext.verify(givenPass, self.pwd)
        except Exception as e:
            log.warning("Pwd failure for {}: {}".format(self.login, e))
        return False

    @property
    def usesGauth(self):
        return self.gauth_key not in ("", None)

    @property
    def avatarUrl(self):
        return self.getAvatarUrl(50)

    def getAvatarUrl(self, size=None):
        if size:
            sizeParam = "s={}&".format(size)
        else:
            sizeParam = ""
        hash = md5(self.email.encode('utf-8')).hexdigest()
        return "//gravatar.com/avatar/{}?{}d=wavatar".format(hash, sizeParam)

    def logout(self):
        pass


class UserPasswordReset(Base):
    """Tokens generated when a user requests a password reset"""
    __tablename__ = 'userpasswordreset'
    id              = Column(String(40), primary_key=True)
    user_id         = Column(Integer, ForeignKey('user.id'))
    user            = relationship("User")
    from_ip         = Column(String(45)) # track IP address fwiw
    expires         = Column(DateTime)
    is_used         = Column(Boolean)

    def __init__(self, user, expiry, usersIP):
        Base.__init__(self)
        self.id       = ShortUUID().uuid()
        self.user     = user
        self.from_ip  = usersIP
        self.expires  = expiry
        self.is_used  = False

    def __str__(self):
        return self.id

    @classmethod
    def getByToken(cls, token):
        try:
            return DBSession.query(cls).\
                    filter(UserPasswordReset.id == token).\
                    filter(UserPasswordReset.is_used == False).\
                    filter(UserPasswordReset.expires > datetime.utcnow()).\
                    one()
        except (NoResultFound, MultipleResultsFound):
            return None

