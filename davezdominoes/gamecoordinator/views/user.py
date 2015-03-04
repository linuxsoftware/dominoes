#---------------------------------------------------------------------------
# Registration, User & Reset User Password Views
#---------------------------------------------------------------------------
from pyramid.httpexceptions import HTTPForbidden
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPNotImplemented
from pyramid.view import view_config
from pyramid.renderers import render
from wtforms.fields import PasswordField
from wtforms.fields import StringField
from wtforms.validators import EqualTo
from wtforms.validators import InputRequired
from wtforms.validators import Length
from wtforms.validators import ValidationError
from wtforms.validators import Regexp
from wtforms_components import Unique # === wtforms_alchemy.Unique 
from wtforms_components import Email
from pyramid_mailer import get_mailer
from ..utils import launchPostMail
from pyramid_mailer.message import Message
from ..utils.formsextns import DisabledBooleanField
from ..utils.formsextns import DisabledIntegerField
from ..utils.formsextns import DisabledStringField
from ..utils.formsextns import PyramidForm
from ..utils.formsextns import SubmitBtns
from ..utils.gauth import genKey, getSecret, getQRCode
from ..models import DBSession
from ..models import User

import logging
log = logging.getLogger(__name__)
import smtplib
log.write = log.debug
smtplib.stderr = log


NewLoginValid     = [Regexp("^[a-zA-Z0-9]+$", 0,
                            "Must be one word of letters and numbers only"),
                     Unique(User.login, DBSession)]
NewPasswordValid  = [InputRequired(), Length(min=5, max=200)]
PasswordConfirmed = [EqualTo('password', "New password doesn't match"),
                     Length(max=200)]
EmailAddressValid = [Email(), Unique(User.email, DBSession)]

# inherit from a BaseUserForm??
class NewUserForm(PyramidForm):
    login     = StringField("Login", NewLoginValid,
                            [lambda n: n.lower() if n else None])
    name      = StringField("Name")
    email     = StringField("Email", EmailAddressValid)
    password  = PasswordField("Password", NewPasswordValid)
    password2 = PasswordField("Confirm Password", PasswordConfirmed)

    def handleOk(self, request, retval):
        self.populate_obj(self.obj)
        self.save()
        emailAddressConfirmation(self.obj, request)
        return HTTPFound(location = request.route_url('registered'))

@view_config(route_name="register",
             http_cache=0,
             renderer='new_user.mako')
def newUser(request):
    log.debug("Register new user screen")
    form = NewUserForm(User())
    form.cancelUrl = request.route_url('login')
    return form.handle(request)

def emailAddressConfirmation(user, request):
    textContent = render('registered_email_text.mako',
                         {'token'     : user.email_confirm,
                          'login'     : user.login,
                          'name'      : user.name},
                        request)
    message = Message(subject="Confirm your email address for Davez Dominoes",
                      recipients=[user.email],
                      body=textContent)
    mailer = get_mailer(request)
    log.info("Queueing activation email to %s" % user.email)
    mailer.send_to_queue(message)
    launchPostMail(request.registry.settings)

@view_config(route_name='registered',
             renderer='registered.mako')
def registered(request):
    log.debug("Registered email sent screen")
    btns = SubmitBtns(request.POST)
    if request.method == 'POST':
        if btns.okBtn.data:
            return HTTPFound(location = request.route_url('login'))
    return { 'btns': btns }

@view_config(route_name='activate',
             renderer='activate.mako')
def activate(request):
    token = request.matchdict['token']
    log.debug("Activate screen for token %s" % token)
    btns = SubmitBtns(request.POST)
    btns.okBtn.disabled = True
    if request.method == 'POST':
        if btns.validate() and btns.okBtn.data:
            return HTTPFound(location = request.route_url('login'))
    else:
        user = User.getByEmailConfirmation(token)
        if user:
            log.debug("Valid token for user {}".format(user))
            user.is_active = True
            btns.okBtn.disabled = False
        else:
            log.debug("Invalid token %s" % token)
    return { 'user': user, 'btns': btns }

class EditUserForm(PyramidForm):
    login           = DisabledStringField("Login")
    name            = StringField("Name")
    email           = StringField("Email", EmailAddressValid)
    failed_logins   = DisabledIntegerField("Failed Logins")
    usesGauth       = DisabledBooleanField("Uses GAuth")

@view_config(route_name="user",
             http_cache=0,
             renderer='edit_user.mako',
             permission='edit')
def editUser(request):
    log.debug("Edit user screen for %s" % request.user)
    form = EditUserForm(request.user)
    form.cancelUrl = \
    form.okUrl     = request.route_url('games')
    form.btns.addBtn.label.text = "Set GAuth"
    form.addUrl = request.route_url('setgauth')
    form.btns.modBtn.label.text = "Change Password"
    form.modUrl = request.route_url('changepwd')
    return form.handle(request)

class ChangePwdForm(PyramidForm):
    oldPassword = PasswordField("Old Password",
                                [InputRequired(), Length(max=200)])
    password    = PasswordField("New Password", NewPasswordValid)
    password2   = PasswordField("Confirm New Password", PasswordConfirmed)

    def validate_oldPassword(self, field):
        if not self.obj.verifyPassword(field.data):
            log.warning("Wrong pwd for %s in change password screen" % self.obj)
            raise ValidationError("Incorrect old password")

@view_config(route_name="changepwd",
             renderer='change_pwd.mako',
             permission='edit')
def changePwd(request):
    log.debug("Change password screen for %s" % request.user)
    form = ChangePwdForm(request.user)
    form.cancelUrl = \
    form.okUrl     = request.route_url('user')
    return form.handle(request)

@view_config(route_name="setgauth",
             renderer='set_gauth.mako',
             permission='edit')
def setGoogleAuth(request):
    log.debug("Set gauth screen for %s" % request.user)
    user = request.user
    btns = SubmitBtns(request.POST)
    btns.delBtn.label.text = "Delete GAuth"
    btns.delBtn.disabled = not user.usesGauth
    gauthUrl = request.route_url('gauth.png')

    if request.method == 'POST':
        if not btns.validate():
            log.info("Validation failed in setGoogleAuth")
            if btns.csrfToken.errors:
                log.info("CSRF token failed in login")
            return HTTPForbidden()
        newKey = request.session.get('newgauth')
        if newKey is None:
            log.warning("No gauth key saved in session for setGoogleAuth POST")
            return HTTPForbidden()
        if btns.okBtn.data:
            log.debug("Set gauth to {}".format(newKey))
            user.gauth_key = newKey
        elif btns.delBtn.data:
            user.gauth_key = None
        elif btns.cancelBtn.data:
            pass
        elif btns.hiddenBtn.data:
            # redisplay the same secret
            secret = getSecret(newKey, user.id)
            return {'secret':    secret,
                    'gauthUrl':  gauthUrl,
                    'btns':      btns}
        else:
            return HTTPNotImplemented()
        return HTTPFound(location = request.route_url('user'))

    newKey = genKey()
    request.session['newgauth'] = newKey
    secret = getSecret(newKey, user.id)
    return {'secret':    secret,
            'gauthUrl':  gauthUrl,
            'btns':      btns}

@view_config(route_name="gauth.png",
             renderer="png",
             permission='edit')
def qrcodeImg(request):
    newKey = request.session.get('newgauth')
    if newKey is None:
        log.info("No gauth key saved in session for gauth.png")
        return HTTPForbidden()
    return getQRCode(newKey, request.user)
