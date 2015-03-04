<%inherit file="main.mako" />

<main id="login">
  <form action="${url}" method="post">
    <div class="message">${message}</div>
    ${form.cameFrom}
    <div class="field">
      ${form.password.label}
      ${form.password(maxlength=200)}
    </div>
    <div class="tool-bar">
      ${form.csrfToken}
      ${form.okBtn}
    </div>
  </form>
</main>

<%def name="javascript()">
</%def>

