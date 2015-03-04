<%inherit file="main.mako" />

<main id="reset-password">
  <h2>Reset Password:</h2>
  <form method="POST" action="${req.path_url}" enctype="multipart/form-data">
    <p class="explain-resetpwd">
      Enter either of your email address or your login in the field below
      and we will send you an email explaining how to reset your password
      (and also tell you what your login is).
    </p>

    %if form.errors:
      <ul class="errors">
        %for field, errors in form.errors.items():
            %for error in errors:
                <li>${form[field].label}: ${error}</li>
            %endfor
        %endfor
      </ul>
    %endif
    <div class="password">
      <div class="field">
        ${form.nameOrEmail.label}
        ${form.nameOrEmail(maxlength=100)}
      </div>
    </div> 
    <div class="tool-bar">
      ${btns.csrfToken}
      ${btns.hiddenBtn}
      ${btns.cancelBtn}
      ${btns.okBtn}
    </div>
  </form>
</div>

<%def name="javascript()">
</%def>

