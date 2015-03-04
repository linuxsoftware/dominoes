<%inherit file="main.mako" />

<main id="edit-user">
  <h2>User Settings:</h2>
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
    <div class="user">
      %for field in form:
        <div class="field">
          ${field.label} ${field(**field.extattrs)}
        </div>
      %endfor
        <div class="field">
          <label class="avatar-label">Avatar</label>
          <img src="${req.user.avatarUrl}" alt="" class="gravatar" />
          <div class="explain-gravatar">
             We get your avatar image from 
             <a href="//gravatar.com">gravatar.com</a>.
             To change it, create an account &amp; login there.
           </div>
        </div>
    </div> <!-- user -->
    <div class="tool-bar">
      ${btns.csrfToken}
      ${btns.hiddenBtn}
      ${btns.addBtn}
      ${btns.modBtn}
      ${btns.cancelBtn}
      ${btns.okBtn}
    </div>
  </form>
</main>
