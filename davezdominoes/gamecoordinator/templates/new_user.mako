<%inherit file="main.mako" />

<main id="new-user">
  <h2>Register:</h2>
  <form method="POST" action="${req.path_url}" enctype="multipart/form-data">
    %if form.errors:
      <ul class="errors">
        %for field, errors in form.errors.items():
          %for error in errors:
            <li>${form[field].label}: ${error}</li>
          %endfor
        %endfor
      </ul>
    %endif
    <div class="field">
      ${form.login.label}
      ${form.login(autofocus=True, maxlength=20)}
    </div>
    <div class="field">
      ${form.name.label}
      ${form.name(maxlength=80)}
    </div>
    <div class="field">
      ${form.email.label}
      ${form.email(maxlength=100)}
    </div>
    <div class="field">
      ${form.password.label}
      ${form.password(maxlength=200)}
    </div>
    <div class="field">
      ${form.password2.label}
      ${form.password2(maxlength=200)}
    </div>
    <div class="tool-bar">
      ${btns.csrfToken}
      ${btns.hiddenBtn}
      ${btns.cancelBtn}
      ${btns.okBtn}
    </div>
  </form>
</main>

<%def name="javascript()">
</%def>

