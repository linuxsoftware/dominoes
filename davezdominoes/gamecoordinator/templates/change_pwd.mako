<%inherit file="main.mako" />

<main id="change-password">
  <h2>Change Password:</h2>
  <form method="POST" action="${req.path_url}"
   enctype="multipart/form-data">
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
      %for field in form:
          <div class="field">
            ${field.label} ${field(maxlength=200)}
          </div>
      %endfor
    </div>
    <div class="tool-bar">
      ${btns.csrfToken}
      ${btns.hiddenBtn}
      ${btns.cancelBtn}
      ${btns.okBtn}
    </div>
  </form>
</main>
