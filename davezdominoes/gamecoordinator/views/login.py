# ------------------------------------------------------------------------------
# Login/Logout Views
# ------------------------------------------------------------------------------
import os
from datetime import datetime, timedelta
from pyramid.httpexceptions import HTTPNotFound
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPNotImplemented
from pyramid.renderers import render, render_to_response
from pyramid.response import Response
from pyramid.security import forget
from pyramid.security import remember
from pyramid.view import forbidden_view_config
from pyramid.view import view_config
from pyramid_mailer import get_mailer
from ..utils import launchPostMail
from pyramid_mailer.message import Message
from wtforms import Form
from wtforms.fields import HiddenField
from wtforms.fields import StringField
from wtforms.fields import PasswordField
from wtforms.fields import SubmitField
from ..utils.formsextns import DisabledPasswordField
from ..utils.formsextns import SecureForm
from ..utils.formsextns import PyramidForm
from wtforms.validators import InputRequired
from wtforms.validators import Length
from wtforms.validators import ValidationError
from ..utils.formsextns import SubmitBtns
from ..security import checkAuthentication, checkVerification, Authentication
from ..models import DBSession
from ..models import User
from ..models import UserPasswordReset
from .user import NewPasswordValid, PasswordConfirmed

import logging
log = logging.getLogger(__name__)


@forbidden_view_config()
def forbidden(request):
    log.debug("Forbidden request to {}".format(request.url))
    user = request.user
    if user is None:
        return login(request)
    elif user.usesGauth and not user.gauthVerified:
        return verifyUser(request)
    else:
        log.debug("Forbidden user is {}".format(request.user.login))
        # return 404 NotFound instead of 403 Forbidden, so we are not leaking
        # the information that there even is a secure page there
        return HTTPNotFound(request.path)

class LoginForm(SecureForm):
    cameFrom = HiddenField()
    login    = StringField(validators=[Length(max=200)])
    password = PasswordField(validators=[Length(max=200)])
    loginBtn = SubmitField("Login")

class VerifyForm(Form):
    cameFrom = HiddenField()
    password = PasswordField(validators=[Length(max=200)])
    okBtn    = SubmitField("OK")

@view_config(route_name='login')
def login(request):
    log.debug("Login screen")
    loginUrl = request.route_url('login')
    referrer = request.url
    if referrer == loginUrl:
        referrer = '/' # never use the login form itself as came_from
    values = {'message':    '',
              'url':        loginUrl}
    form = LoginForm(request.POST, cameFrom = referrer)
    if request.method == 'POST':
        login    = form.login.data.lower()
        password = form.password.data
        if not form.validate():
            log.info("Login validation failed")
            if form.csrfToken.errors:
                log.info("CSRF token failed in login")
            password = None
        if form.loginBtn.data:
            result, user = checkAuthentication(login, password)
            if result in (Authentication.OK, Authentication.TO_VERIFY):
                request.session['loginMethod'] = User.loginMethod
                headers = remember(request, login)
                if result == Authentication.OK:
                    return HTTPFound(location = form.cameFrom.data,
                                     headers  = headers)
                else: # result == Authentication.TO_VERIFY:
                    values["form"] = VerifyForm(request.POST)
                    return Response(render("verify.mako", values, request),
                                    headers = headers)
            elif result == Authentication.LOCKED_OUT:
                values["message"] = "Too many attempts, failed login.  " \
                                    "Contact the webmaster to "          \
                                    "have your account reset."
            else:
                values["message"] = "Failed login"
        else:
            return HTTPNotImplemented()
    values['form'] = form
    return render_to_response('login.mako', values, request)

@view_config(route_name='login',  userNeedsVerification=True)
@view_config(route_name='games',  userNeedsVerification=True)
def verifyUser(request):
    # for 2 factor authentication
    log.debug("Verify User screen")
    loginUrl = request.route_url('login')
    referrer = request.url
    if referrer == loginUrl:
        referrer = '/' # never use the login form itself as came_from
    form = LoginForm(request.POST,
                     cameFrom = referrer,
                     meta={'csrf_context': request.session})
    values = {'message':    '',
              'form':       form,
              'url':        loginUrl}
    if request.method == 'POST':
        givenOtp = form.password.data
        if not form.validate():
            log.info("Login validation failed")
            if form.csrf_token.errors:
                log.info("CSRF token failed in verifyUser")
            givenOtp = None
        if form.okBtn.data:
            result = checkVerification(request.user, givenOtp)
            if result == Authentication.OK:
                log.info("{} verified OK".format(request.user))
                request.verifyUser()
                return HTTPFound(location = form.cameFrom.data)
            elif result == Authentication.LOCKED_OUT:
                values['message'] = 'Too many attempts, failed verification'
            else:
                values['message'] = 'Failed verification'
        else:
            return HTTPNotImplemented()
    return render_to_response('verify.mako', values, request)

class ForgotPwdForm(PyramidForm):
    nameOrEmail = StringField("Login or Email",
                              [InputRequired(), Length(max=100)])

    def validate_nameOrEmail(self, field):
        user = User.getByLogin(field.data)
        if user is None:
            user = User.getByEmail(field.data)
        if user is None:
            raise ValidationError("No such user")
        if not user.email:
            raise ValidationError("User does not have email")
        self.obj = user

    def handleOk(self, request, retval):
        log.debug("ForgotPwdForm OK Button pushed")
        user = self.obj
        emailPwdResetToken(user, request)
        return HTTPFound(location = request.route_url('pwdemailsent'))

@view_config(route_name='forgotpwd',
             renderer='forgot_pwd.mako')
def forgotPassword(request):
    log.debug("Forgot Password screen")
    form = ForgotPwdForm()
    form.cancelUrl = request.route_url('login')
    return form.handle(request);

def emailPwdResetToken(user, request):
    someTime = datetime.utcnow() + timedelta(minutes=30)
    usersIP  = request.environ.get('X-Real-IP', request.remote_addr)
    reset = UserPasswordReset(user, someTime, usersIP)
    DBSession.add(reset)
    log.info("Created reset token %s for %s valid until %s" 
                  % (reset.id, usersIP, someTime))
    textContent = render('reset_pwd_email_text.mako',
                         {'token'     : reset.id,
                          'expires'   : reset.expires,
                          'login'     : user.login,
                          'name'      : user.name},
                        request)
    message = Message(subject="Password reset requested",
                      recipients=[user.email],
                      body=textContent)
    mailer = get_mailer(request)
    log.info("Queueing reset password email to %s" % user.email)
    mailer.send_to_queue(message)
    launchPostMail(request.registry.settings)

@view_config(route_name='pwdemailsent',
             renderer='pwd_email_sent.mako')
def mailSent(request):
    log.debug("Reset password email sent screen")
    btns = SubmitBtns(request.POST)
    if request.method == 'POST':
        if btns.validate() and btns.okBtn.data:
            return HTTPFound(location = request.route_url('login'))
    return { 'btns': btns }

class ResetPwdForm(PyramidForm):
    password    = DisabledPasswordField("New Password", NewPasswordValid)
    confirm     = DisabledPasswordField("Confirm New Password", PasswordConfirmed)

    def handleOk(self, request, retval):
        log.debug("ResetPwdForm OK Button pushed")
        self.obj.is_used = True
        self.obj.user.password = self.password.data
        request.session['loginMethod'] = User.loginMethod
        headers = remember(request, self.obj.user.login.lower())
        return HTTPFound(location = request.route_url('games'),
                         headers  = headers)

@view_config(route_name='resetpwd',
             renderer='reset_pwd.mako')
def resetPassword(request):
    token = request.matchdict['token']
    log.debug("Reset password screen for token %s" % token)
    info = {}
    reset = UserPasswordReset.getByToken(token)
    form = ResetPwdForm(reset)
    form.cancelUrl = request.route_url('user')
    if reset:
        log.debug("Valid token for user {}".format(reset.user))
        info['validtoken']     = True
        form.password.disabled = False
        form.confirm.disabled  = False
    else:
        log.debug("Invalid token %s" % token)
        info['validtoken']       = False
        form.btns.okBtn.disabled = True
    return form.handle(request, info)

@view_config(route_name='logout')
def logout(request):
    log.debug("Logout screen")
    user = request.user
    if user:
        user.logout()
    headers = forget(request)
    request.unverifyUser()
    request.session.clear()
    return HTTPFound(location = request.route_url('games'),
                     headers = headers)

# ------------------------------------------------------------------------------
# Oauth Login and Connect
# ------------------------------------------------------------------------------
@view_config(route_name='altlogin')
def altlogin(UserCls, request):
    log.debug("Alt Auth Login")
    request.session['loginMethod'] = UserCls.loginMethod
    authzUrl = UserCls.authzUrl(request.session.new_csrf_token())
    return HTTPFound(location = authzUrl)

@view_config(route_name='altconnect')
def altconnect(UserCls, request):
    log.debug("Alt Auth Callback")
    loginMethod = request.session.get('loginMethod')
    if loginMethod != UserCls.loginMethod:
        log.warning("Incorrect loginMethod {}".format(loginMethod))
        return HTTPNotFound(request.path)
    code  = request.GET.get('code')
    state = request.GET.get('state')
    if code is None or state != request.session.get_csrf_token():
        log.warning("Invalid GET params {code} {state}".format(**locals()))
        # TODO render the login page with an error message
        return HTTPFound(location = "/")
    headers = None
    user = UserCls.getUser(code)
    if user:
        request.session['oauthToken'] = user.token
        headers = remember(request, user.login)
    return HTTPFound(location = "/", headers = headers)
