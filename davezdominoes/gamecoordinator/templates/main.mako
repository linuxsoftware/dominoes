<!DOCTYPE html>
<html class="no-js">
  <head>
    ${self.head()}
  </head>
  <body>
    <div id="wrapper">
      ${self.header()}
      ${next.body()}
      ${self.footer()}
    </div> <!-- wrapper -->
    ${self.javascript()}
  </body>
</html>

<%def name="head()">
  <meta charset="utf-8">
  <title>Davez Dominoes</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="noindex,nofollow,noarchive" />
  <link rel="icon" type="image/vnd.microsoft.icon" href="/favicon.ico"/>
  %for url in webassets(req, 'stylesheet'):
    <link rel="stylesheet" href="${url}" />
  %endfor
</%def>

<%def name="header()">
  <header>
    <h1><a href="/" title="Home">Davez Dominoes</a></h1>
    ${self.accountInfo()}
  </header>
</%def>

<%def name="navigation()">
  <nav id="topMenu">
    <a href="/" title="Home">Home</a> 
  </nav>
</%def>

<%def name="accountInfo()">
  <div class="account-info">
    %if req.user:
      %if req.has_permission('edit', req.user):
        <a href="/user" title="Account Info">${avatar()}</a>
      %else:
        ${avatar()}
      %endif
      <div class="account-info-links">
        <div class="current-user">
          %if req.has_permission('edit', req.user):
            <a href="/user" title="Account Info">${req.user.name}</a>
          %else:
            <span>${req.user.name}</span>
          %endif
        </div>
        <div class="logout">
          <a href="/logout">Logout</a>
        </div>
      </div>
    %else:
      <div class="account-info-links">
        <div class="current-user">
        </div>
        <div class="login">
          <!--We will always show the login tablet anyway-->
          <!-- <a href="/login">Login</a> -->
        </div>
      </div>
    %endif
  </div>
</%def>

<%def name="avatar()">
          <img src="${req.user.avatarUrl}" 
               width="50" height="50" alt="" class="avatar" />
</%def>

<%def name="background()">
  <div id="background" class="grey"></div>
</%def>

<%def name="footer()">
  <footer>
    <div class="bottom-left">
      <% flashMsgs = req.session.peek_flash() %>
      %if flashMsgs:
        ${flashMsgs[-1]}
      %endif
    </div>
    <div class="bottom-right">
      <a href="http://linuxsoftware.co.nz">LinuxSoftware</a>
    </div>
  </footer>
</%def>

<%namespace file="jslibs.mako" name="jslibs" />
<%def name="javascript()">
  ${jslibs.jquery()}
</%def>

