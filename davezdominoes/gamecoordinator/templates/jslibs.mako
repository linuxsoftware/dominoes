<%def name="javascript()">
  ${jquery()}
  ${jquery_ui()}
  ${jquery_idletimer()}
  ${jquery_datatables()}
</%def>

<%def name="jquery()">
  <script src="//ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js"></script>
  <script>
    if (typeof jQuery === 'undefined') {
        document.write('<script src="/static/js/jquery-2.1.1.min.js">\x3C/script>');
    }
  </script>
</%def>

<%def name="jquery_ui()">
  <script src="//ajax.googleapis.com/ajax/libs/jqueryui/1.11.2/jquery-ui.min.js"></script>
  <script>
    if (typeof jQuery.ui === 'undefined') {
        document.write('<script src="/static/js/jquery-ui.1.11.2.min.js">\x3C/script>');
    }
  </script>
</%def>

<%def name="fabric()">
  <script src="/static/js/fabric-1.4.13.min.js"></script>
  ##<script src="/static/js/fabric-1.4.13.js"></script>
</%def>

<%def name="autobahn()">
  %if req.registry.settings.get('autobahn.debug'):
    <script>AUTOBAHN_DEBUG = true;</script>
  %endif
  <script src="/static/js/autobahn-0.9.5.min.js"></script>
</%def>
