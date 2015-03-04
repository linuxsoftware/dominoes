<%inherit file="main.mako" />

<main id="registered">
  <h2>Email Sent:</h2>
  <form method="POST" action="${req.path_url}" enctype="multipart/form-data">
    <p class="explain-email-activation">
      To activate your account please click on the link that has been emailed 
      to your email addresss.
      (Check it hasn't ended up in your spam folder.)
    </p>

    <div class="tool-bar">
      ${btns.csrfToken}
      ${btns.okBtn}
    </div>
  </form>
</main>
