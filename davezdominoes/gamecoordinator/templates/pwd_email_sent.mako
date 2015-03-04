<%inherit file="main.mako" />

<main id="reset-password">
  <h2>Email Sent:</h2>
  <form method="POST" action="${req.path_url}" enctype="multipart/form-data">
    <p class="explain-resetpwd">
      An email has been sent to your email account, you should have it soon.
      (Also check it hasn't ended up in your spam folder.)
      It says what your login is and explains how to reset your password.
    </p>

    <div class="tool-bar">
      ${btns.csrfToken}
      ${btns.okBtn}
    </div>
  </form>
</main>
