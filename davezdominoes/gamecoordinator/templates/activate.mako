<%inherit file="main.mako" />

<main id="activate">
  %if user:
    <h2>Account activated:</h2>
    <p class="valid-token">
      Your email address has been successfully confirmed.  You may now login.
    </p>
  %else:
    <h2>Invalid token:</h2>
    <p class="invalid-token">
      The token you have is not valid.
    </p>
  %endif
  <form method="POST" action="${req.path_url}" enctype="multipart/form-data">
    <div class="tool-bar">
      ${btns.csrfToken}
      ${btns.okBtn}
    </div>
  </form>
</main>
