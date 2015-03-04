<%inherit file="main.mako" />

<main id="set-gauth">
  <h2>Google Authenticator:</h2>
  <form method="POST" action="${req.path_url}" enctype="multipart/form-data">
    <div class="explain-gauth">
    <p>
      GAuth verification is an optional extra step you can enable if you have
      a smart phone which will increase the security of your account.
    </p>
    <p>
      <a href="http://en.wikipedia.org/wiki/Google_Authenticator">Google Authenticator</a> is an app you install on your phone:
        <a href="https://play.google.com/store/apps/details?id=com.google.android.apps.authenticator2">Android</a>, or 
        <a href="https://itunes.apple.com/nz/app/google-authenticator/id388497605">iPhone</a>.
    </p>
    <p>
      Then scan the QR code shown below into your phone.  
      That saves the seed which the app will use to generate the time based
      one-time-passwords that the system will prompt you for as the second
      step of logging in.
    </p>
    <p>
      When you are shown the prompt "Verify", just type in the 6 digit code
      from the Google Authenticator app on your phone.  
    </p>
    </div>
    <div class="gauth">
       <img src="${gauthUrl}" /> <br/>
       <span=class="gauth-secret">${secret}</span>
    </div> <!-- gauth -->
    <div class="tool-bar">
      ${btns.csrfToken}
      ${btns.hiddenBtn}
      ${btns.cancelBtn}
      ${btns.delBtn}
      ${btns.okBtn}
    </div>
  </form>
</main>
