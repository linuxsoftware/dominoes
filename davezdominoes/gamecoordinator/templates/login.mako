<%inherit file="main.mako" />
<%namespace file="jslibs.mako" name="jslibs" />

<div id="login-wrapper">
  <main id="login-tablet">
    <div class="message">${message}</div>
    <form action="${url}" method="post">
      ${form.cameFrom}
      <div class="field">
        ${form.login.label}
        ${form.login(autofocus=True, maxlength=200)}
      </div>
      <div class="field">
        ${form.password.label}
        ${form.password(maxlength=200)}
      </div>
      <div class="tool-bar">
        <a class="newuser" title="Click here to register as a new user"
           href="/user/register">New User</a>
        <a class="forgotpwd" title="Click here to reset your password"
           href="/resetpwd">Forgot password</a>
        ${form.csrfToken}
        ${form.loginBtn}
      </div>
      <div class="clear-float"></div>

    </form>
  </main>
</div> <!-- login-wrapper -->

<%!
from davezdominoes.gamecoordinator.models import GoogleUser
from davezdominoes.gamecoordinator.models import FacebookUser
from davezdominoes.gamecoordinator.models import GitHubUser
%>
<div id="alt-login-tablet">
  Or login using
  <a href="/login/${GoogleUser.loginMethod}" 
     id="google-signin" class="signin">
    <span class="icon"></span><span class="text">Google</span>
  </a>
  <a href="/login/${FacebookUser.loginMethod}" 
     id="facebook-signin" class="signin">
    <span class="icon"></span><span class="text">Facebook</span>
  </a>
  <a href="/login/${GitHubUser.loginMethod}" 
     id="github-signin" class="signin">
    <span class="icon"></span><span class="text">GitHub</span>
  </a>
</div>

<%def name="javascript()">
  ${jslibs.jquery()}
</%def>

