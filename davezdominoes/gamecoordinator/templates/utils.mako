<%def name="flashmessages()">  
  %for message in req.session.pop_flash():  
    <div class="alert-message fade in">  
      <a class="close" href="#">×</a>  
      ${message}
    </div>  
  %endfor  
</%def>

<%def name="jquery_flashmessages()">
  <script type="text/javascript" charset="utf8">
    $(function () {
      $(".alert-message .close").click(function () {
        $(this).parent().hide();
        return false;
      });   
    });
  </script>
</%def>
