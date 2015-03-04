<%inherit file="main.mako"/>
<%namespace file="jslibs.mako" name="jslibs" />

<main id="games-list">
  %for game in games:
    ${gameTablet(game)}
  %endfor
  <div class="games-padding"></div>
  <div class="games-padding"></div>
</main>

<%def name="gameTablet(game)">
  <div class="game-tablet" id="game-tablet${game.game_server_id}"> 
    <h3>${game.name}</h3> 
    <div class="game-description">
    </div>
    <div class="game-rules">
      <label>Rules:</label>  <span class="rules"></span>
    </div>
    <div class="game-status">
      <label>Status:</label> <span class="status">Not ready</span>
    </div>
    <h4>Players:</h4>
    <ul class="players">
      %for player in game.players:
        <li class="player">
          ${player.name}
        </li>
      %endfor
    </ul>
    <div class="actions">
      <a href="javascript:void(0);" class="join-game">Join</a>
      <a href="javascript:void(0);" class="leave-game">Leave</a>
      <a href="javascript:void(0);" class="start-game">Start</a>
      <a class="play-game" href="${game.url}">Play</a>
    </div>
  </div>
</%def>

<%def name="javascript()">
  ${jslibs.jquery()}
  ${jslibs.autobahn()}
  %for url in webassets(req, 'admin_client'):
    <script src="${url}"></script>
  %endfor
  <script>
    $(function() {
      Dominoes.initialize({
          login:   '${req.user.login}',
          host:    '${req.host}',
          port:    '${req.registry.settings["gameserver.port"]}',
          encrypt: ${"true" if req.scheme=="https" else "false"}})
      Dominoes.admin();
    });
  </script>
</%def>
