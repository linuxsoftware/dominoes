<%inherit file="main.mako"/>
<%namespace file="jslibs.mako" name="jslibs" />

<main id="game">
  <canvas id="playing-area">Your browser is not supported.</canvas>
</main>

<%def name="javascript()">
  ${jslibs.jquery()}
  ${jslibs.fabric()}
  ${jslibs.autobahn()}
  %for url in webassets(req, 'game_client'):
    <script src="${url}"></script>
  %endfor
  <script>
    $(function() {
      Dominoes.initialize({
          login:   '${req.user.login}',
          host:    '${req.host}',
          port:    '${req.registry.settings["gameserver.port"]}',
          encrypt: ${"true" if req.scheme=="https" else "false"}})
      Dominoes.play(${gameId});
    });
  </script>
</%def>
