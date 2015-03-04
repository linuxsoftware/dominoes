<%inherit file="main.mako" />

<main id="reset-password">
  <h2>Reset Password:</h2>
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
    %if not validtoken:
      <div class="invalid-token">
        The token you have is no longer valid.
        Would you like to request a <a href="/resetpwd">new one</a>?
      </div>
    %endif
    <div class="password">
        <div class="field">
          ${form.password.label(class_="is-required")} ${form.password(autofocus=True, maxlength=200)}
        </div>
        <div class="field">
          ${form.confirm.label(class_="is-required")} ${form.confirm(maxlength=200)}
        </div>
    </div>
    <div class="tool-bar">
      ${btns.csrfToken}
      ${btns.okBtn}
    </div>
  </form>
</main>
