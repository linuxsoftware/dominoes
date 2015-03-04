(function() {
  var __indexOf = [].indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };

  Function.prototype.property = function(prop, desc) {
    return Object.defineProperty(this.prototype, prop, desc);
  };

  this.Dominoes = {
    login: "",
    initialize: function(options) {
      if (options == null) {
        options = {};
      }
      $.extend(this, options);
      if (this.host == null) {
        this.host = "127.0.0.1";
      }
      if (this.port == null) {
        this.port = 9000;
      }
      if (this.encrypt == null) {
        this.encrypt = false;
      }
      if (this.scheme == null) {
        this.scheme = this.encrypt ? "wss" : "ws";
      }
      this.url = "" + this.scheme + "://" + this.host + ":" + this.port;
      return console.log("Dominoes GameServer @ " + this.url);
    }
  };

  Dominoes.GameTablet = (function() {
    function GameTablet(myDiv, gameId) {
      var myDivId;
      this.myDiv = myDiv;
      this.gameId = gameId;
      myDivId = this.myDiv.attr('id');
      console.log("new GameTablet " + this.gameId + " #" + myDivId);
    }

    GameTablet.prototype.connect = function() {
      var conn;
      conn = new autobahn.Connection({
        url: Dominoes.url,
        realm: "game" + this.gameId,
        authmethods: ["beaker"]
      });
      conn.onopen = (function(_this) {
        return function(session) {
          _this.session = session;
          console.log("Connected to " + Dominoes.url);
          _this.session.prefix("dominoes", "nz.net.software.dominoes");
          _this.session.subscribe("dominoes:update", _this.onUpdate.bind(_this));
          _this.myDiv.find(".join-game").click(function() {
            return _this.session.call("dominoes:join");
          });
          _this.myDiv.find(".leave-game").click(function() {
            return _this.session.call("dominoes:leave");
          });
          _this.myDiv.find(".start-game").click(function() {
            return _this.session.call("dominoes:start");
          });
          return _this.session.call("dominoes:poke");
        };
      })(this);
      return conn.open();
    };

    GameTablet.prototype.onUpdate = function(args, kwargs, dtl) {
      var avatar, kickLink, login, name, player, playerItem, playersList, _i, _len, _ref, _ref1, _ref2;
      console.log("Got an update");
      this.myDiv.find("span.status").text(kwargs.status);
      this.myDiv.find("span.rules").text(kwargs.rules);
      playersList = this.myDiv.find(".players");
      playersList.empty();
      _ref = kwargs.players;
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        _ref1 = _ref[_i], login = _ref1[0], name = _ref1[1], avatar = _ref1[2];
        playerItem = $('<li>');
        avatar = $('<img src="' + avatar + '" alt="&nbsp;&nbsp;&nbsp;&nbsp;" width="16" height="16"/>');
        playerItem.append(avatar);
        playerItem.append(' ' + name + ' ');
        if (Dominoes.login === kwargs.players[0][0] && Dominoes.login !== login) {
          kickLink = $(' <a href="javascript:void(0);" class="kick">Kick</a>');
          playerItem.append(kickLink);
        }
        playersList.append(playerItem);
      }
      this.myDiv.find(".actions a").hide();
      if (_ref2 = Dominoes.login, __indexOf.call((function() {
        var _j, _len1, _ref3, _results;
        _ref3 = kwargs.players;
        _results = [];
        for (_j = 0, _len1 = _ref3.length; _j < _len1; _j++) {
          player = _ref3[_j];
          _results.push(player[0]);
        }
        return _results;
      })(), _ref2) >= 0) {
        this.myDiv.addClass("playing");
        if (kwargs.status === "Started") {
          this.myDiv.find(".play-game").show();
        } else {
          this.myDiv.find(".leave-game").show();
        }
      } else {
        this.myDiv.removeClass("playing");
        this.myDiv.find(".join-game").show();
      }
      if (kwargs.status === "Ready") {
        if (kwargs.players && kwargs.players[0][0] === Dominoes.login) {
          this.myDiv.find(".start-game").show();
        }
      }
    };

    return GameTablet;

  })();

  Dominoes.admin = function() {
    var prefix;
    prefix = "game-tablet";
    $("div[id^='" + prefix + "']").each(function() {
      var gameId, tablet;
      gameId = $(this).attr('id').substr(prefix.length);
      tablet = new Dominoes.GameTablet($(this), gameId);
      $(this).data('dominoes_object', tablet);
      tablet.connect();
    });
  };

}).call(this);
