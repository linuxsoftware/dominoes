(function() {
  var Bone, Hand, PlayingArea, Run, radiansToDegrees;

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

  Run = (function() {
    function Run(game, startBoneId) {
      var bone, dots;
      this.game = game;
      dots = startBoneId.split("|");
      bone = new Bone({
        game: this.game,
        left: 400,
        top: 250,
        leftDots: parseInt(dots[0]),
        rightDots: parseInt(dots[1])
      });
      this.bones = [bone];
      this.insideBone = bone;
      this.outsideBone = bone;
      this.game.area.add(bone);
      return;
    }

    return Run;

  })();

  Hand = (function() {
    function Hand(game) {
      this.game = game;
      this.bones = [];
    }

    Hand.prototype.draw = function(boneIds) {
      var bone, boneId, dots, i, _i, _j, _len, _len1, _ref;
      for (i = _i = 0, _len = boneIds.length; _i < _len; i = ++_i) {
        boneId = boneIds[i];
        dots = boneId.split("|");
        bone = new Bone({
          game: this.game,
          left: 100 + i * 60,
          top: 450,
          leftDots: parseInt(dots[0]),
          rightDots: parseInt(dots[1]),
          isMoveable: true
        });
        bone.left = 800;
        bone.top = 0;
        this.game.area.add(bone);
        this.bones.push(bone);
      }
      _ref = this.bones;
      for (_j = 0, _len1 = _ref.length; _j < _len1; _j++) {
        bone = _ref[_j];
        bone.reset();
      }
    };

    return Hand;

  })();

  Dominoes.Game = (function() {
    function Game(gameId) {
      var boneBg;
      this.gameId = gameId;
      console.log("new Game " + this.gameId);
      this.area = new PlayingArea("playing-area", {
        game: this,
        width: 800,
        height: 500,
        selection: false
      });
      this.hand = void 0;
      this.run = void 0;
      this.my = {};
      boneBg = false;
      if (boneBg) {
        fabric.util.loadImage(boneBg, (function(_this) {
          return function(img) {
            if (img) {
              Bone.prototype.fill = new fabric.Pattern({
                source: img,
                offsetX: 26,
                offsetY: 14
              });
              return _this.area.renderAll();
            }
          };
        })(this));
      }
    }

    Game.prototype.connect = function() {
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
          return _this.session.call("dominoes:ready").then(_this.inGame.bind(_this));
        };
      })(this);
      return conn.open();
    };

    Game.prototype.inGame = function(retval) {
      var bones, kwargs, _ref;
      console.log("begin play");
      kwargs = retval.kwargs;
      _ref = kwargs.player, this.my.login = _ref[0], this.my.name = _ref[1], this.my.avatarUrl = _ref[2], bones = _ref[3];
      this.hand = new Hand(this);
      this.hand.draw(bones);
      this.run = new Run(this, kwargs.start);
    };

    Game.prototype.onUpdate = function(args, kwargs, dtl) {};

    return Game;

  })();

  Dominoes.play = function(gameId) {
    var game;
    game = new Dominoes.Game(gameId);
    game.connect();
  };

  PlayingArea = fabric.util.createClass(fabric.Canvas, {
    initialize: function(canvasId, options) {
      if (options == null) {
        options = {};
      }
      this.callSuper("initialize", canvasId, options);
      this.selectedBone = null;
      this.game = options.game;
      return this.on("mouse:down", this.onMouseDown);
    },
    onMouseDown: function(op) {
      if (op.target instanceof Bone && op.target.isMoveable) {
        this.selectedBone = op.target;
        this.onMouseMove(op);
        this.on("mouse:move", this.onMouseMove);
        return this.on("mouse:up", this.onMouseUp);
      }
    },
    onMouseMove: function(op) {
      var here;
      here = this.getPointer(op.e);
      this.selectedBone.moveTo(here);
      this.game.session.publish("dominoes:move", [here]);
      if (this.selectedBone.intersectsWithObject(this.game.run.insideBone)) {
        return this.fooTouch(this.selectedBone, this.game.run.insideBone);
      }
    },
    fooTouch: function(left, right) {},
    onMouseUp: function(op) {
      this.selectedBone.reset();
      this.game.session.publish("dominoes:drop");
      this.selectedBone = null;
      this.off("mouse:move", this.onMouseMove);
      return this.off("mouse:up", this.onMouseUp);
    }
  });

  radiansToDegrees = fabric.util.radiansToDegrees;

  Bone = fabric.util.createClass(fabric.Rect, {
    type: "bone",
    left: 100,
    top: 100,
    width: 53,
    height: 28,
    stroke: "#656565",
    fill: "#d0d0d0",
    hasControls: false,
    hasBorders: false,
    originX: "center",
    originY: "center",
    lockMovementX: true,
    lockMovementY: true,
    isMoveable: false,
    initialize: function(options) {
      if (options == null) {
        options = {};
      }
      this.callSuper("initialize", options);
      this.leftDots = options.leftDots;
      this.rightDots = options.rightDots;
      this.origPos = new fabric.Point(this.left, this.top);
      this.amMoving = false;
    },
    dragTo: function(op) {
      var dragged;
      if (this.isMoveable) {
        dragged = this.game.area.getPointer(op.e);
        this.moveTo(dragged);
        this.game.session.publish("dominoes:move", [dragged]);
      }
    },
    endDrag: function() {
      if (this.isMoveable) {
        this.reset();
        this.game.session.publish("dominoes:drop");
      }
    },
    recvMove: function(args) {
      this.moveTo(args[0]);
      this.game.area.renderAll();
    },
    recvDrop: function(args) {
      this.reset();
    },
    moveTo: function(dragged) {
      var angle, center;
      center = this.getCenterPoint();
      if (!this.amMoving) {
        this.amMoving = true;
        if (dragged.x < center.x) {
          this.clickedLeft = true;
        }
        this.game.area.bringToFront(this);
        this.setShadow("4px 4px 8px rgba(0,0,0,0.2)");
      }
      if (dragged.x < this.width / 2) {
        dragged.x = this.width / 2;
      }
      if (dragged.x > this.game.area.width - this.width / 2) {
        dragged.x = this.game.area.width - this.width / 2;
      }
      if (dragged.y < this.width / 2) {
        dragged.y = this.width / 2;
      }
      if (dragged.y > this.game.area.height - this.width / 2) {
        dragged.y = this.game.area.height - this.width / 2;
      }
      angle = Math.atan2(dragged.x - center.x, center.y - dragged.y);
      if (this.clickedLeft) {
        angle += Math.PI / 2;
        this.left = dragged.x + Math.cos(angle) * this.width / 4;
        this.top = dragged.y + Math.sin(angle) * this.width / 4;
      } else {
        angle -= Math.PI / 2;
        this.left = dragged.x - Math.cos(-angle) * this.width / 4;
        this.top = dragged.y + Math.sin(-angle) * this.width / 4;
      }
      this.angle = radiansToDegrees(angle);
    },
    attachesTo: function(other) {
      return false;
    },
    reset: function() {
      var angle, center;
      center = this.getCenterPoint();
      angle = Math.atan2(center.x - this.origPos.x, this.origPos.y - center.y);
      if (this.clickedLeft) {
        angle += Math.PI / 2;
      } else {
        angle -= Math.PI / 2;
      }
      this.animate("angle", radiansToDegrees(angle), {
        duration: 50,
        onChange: (function(_this) {
          return function() {
            return _this.game.area.renderAll();
          };
        })(this),
        onComplete: (function(_this) {
          return function() {
            var animation, finalAngle, props;
            if (_this.angle < -180) {
              finalAngle = -360;
            } else if (_this.angle > 180) {
              finalAngle = 360;
            } else {
              finalAngle = 0;
            }
            props = {
              "left": _this.origPos.x,
              "top": _this.origPos.y,
              "angle": finalAngle
            };
            animation = {
              duration: 120,
              onChange: _this.game.area.renderAll.bind(_this.game.area),
              onComplete: function() {
                _this.setShadow(null);
                _this.game.area.sendToBack(_this);
                _this.game.area.renderAll();
                _this.clickedLeft = false;
                _this.amMoving = false;
                _this.angle = 0;
              }
            };
            _this.animate(props, animation);
          };
        })(this)
      });
    },
    _render: function(ctx) {
      this.callSuper("_render", ctx);
      ctx.save();
      ctx.translate(-this.width / 4, 0);
      this._drawDots(ctx, this.leftDots);
      ctx.translate(this.width / 2, 0);
      this._drawDots(ctx, this.rightDots);
      ctx.restore();
    },
    _drawDots: function(ctx, numDots) {
      switch (numDots) {
        case 0:
          break;
        case 1:
          ctx.fillStyle = "#088587";
          this._drawDot(ctx, 0, 0);
          break;
        case 2:
          ctx.fillStyle = "#21a603";
          this._drawDot(ctx, -0.25, -0.5);
          this._drawDot(ctx, 0.25, 0.5);
          break;
        case 3:
          ctx.fillStyle = "#ff636e";
          this._drawDot(ctx, -0.25, -0.5);
          this._drawDot(ctx, 0, 0);
          this._drawDot(ctx, 0.25, 0.5);
          break;
        case 4:
          ctx.fillStyle = "#ab593d";
          this._drawDot(ctx, -0.25, -0.5);
          this._drawDot(ctx, 0.25, -0.5);
          this._drawDot(ctx, -0.25, 0.5);
          this._drawDot(ctx, 0.25, 0.5);
          break;
        case 5:
          ctx.fillStyle = "#0863bf";
          this._drawDot(ctx, -0.25, -0.5);
          this._drawDot(ctx, 0.25, -0.5);
          this._drawDot(ctx, 0, 0);
          this._drawDot(ctx, -0.25, 0.5);
          this._drawDot(ctx, 0.25, 0.5);
          break;
        case 6:
          ctx.fillStyle = "#ffb31a";
          this._drawDot(ctx, -0.33, -0.5);
          this._drawDot(ctx, 0, -0.5);
          this._drawDot(ctx, 0.33, -0.5);
          this._drawDot(ctx, -0.33, 0.5);
          this._drawDot(ctx, 0, 0.5);
          this._drawDot(ctx, 0.33, 0.5);
          break;
        case 7:
          ctx.fillStyle = "#d5288f";
          this._drawDot(ctx, -0.33, -0.52);
          this._drawDot(ctx, 0, -0.52);
          this._drawDot(ctx, 0.33, -0.52);
          this._drawDot(ctx, 0, 0);
          this._drawDot(ctx, -0.33, 0.52);
          this._drawDot(ctx, 0, 0.52);
          this._drawDot(ctx, 0.33, 0.52);
          break;
        case 8:
          ctx.fillStyle = "#0b928c";
          this._drawDot(ctx, -0.33, -0.52);
          this._drawDot(ctx, 0, -0.52);
          this._drawDot(ctx, 0.33, -0.52);
          this._drawDot(ctx, -0.33, 0);
          this._drawDot(ctx, 0.33, 0);
          this._drawDot(ctx, -0.33, 0.52);
          this._drawDot(ctx, 0, 0.52);
          this._drawDot(ctx, 0.33, 0.52);
          break;
        case 9:
          ctx.fillStyle = "#5b2d55";
          this._drawDot(ctx, -0.33, -0.52);
          this._drawDot(ctx, 0, -0.52);
          this._drawDot(ctx, 0.33, -0.52);
          this._drawDot(ctx, -0.33, 0);
          this._drawDot(ctx, 0, 0);
          this._drawDot(ctx, 0.33, 0);
          this._drawDot(ctx, -0.33, 0.52);
          this._drawDot(ctx, 0, 0.52);
          this._drawDot(ctx, 0.33, 0.52);
          break;
        case 10:
          ctx.fillStyle = "#f79035";
          this._drawDot(ctx, -0.34, -0.55);
          this._drawDot(ctx, -0.116, -0.55);
          this._drawDot(ctx, 0.116, -0.55);
          this._drawDot(ctx, 0.34, -0.55);
          this._drawDot(ctx, -0.34, 0);
          this._drawDot(ctx, 0.34, 0);
          this._drawDot(ctx, -0.34, 0.55);
          this._drawDot(ctx, -0.116, 0.55);
          this._drawDot(ctx, 0.116, 0.55);
          this._drawDot(ctx, 0.34, 0.55);
          break;
        case 11:
          ctx.fillStyle = "#641223";
          this._drawDot(ctx, -0.34, -0.55);
          this._drawDot(ctx, -0.116, -0.55);
          this._drawDot(ctx, 0.116, -0.55);
          this._drawDot(ctx, 0.34, -0.55);
          this._drawDot(ctx, -0.34, 0);
          this._drawDot(ctx, 0, 0);
          this._drawDot(ctx, 0.34, 0);
          this._drawDot(ctx, -0.34, 0.55);
          this._drawDot(ctx, -0.116, 0.55);
          this._drawDot(ctx, 0.116, 0.55);
          this._drawDot(ctx, 0.34, 0.55);
          break;
        case 12:
          ctx.fillStyle = "#cc6663";
          this._drawDot(ctx, -0.34, -0.55);
          this._drawDot(ctx, -0.116, -0.55);
          this._drawDot(ctx, 0.116, -0.55);
          this._drawDot(ctx, 0.34, -0.55);
          this._drawDot(ctx, -0.34, 0);
          this._drawDot(ctx, -0.116, 0);
          this._drawDot(ctx, 0.116, 0);
          this._drawDot(ctx, 0.34, 0);
          this._drawDot(ctx, -0.34, 0.55);
          this._drawDot(ctx, -0.116, 0.55);
          this._drawDot(ctx, 0.116, 0.55);
          this._drawDot(ctx, 0.34, 0.55);
      }
    },
    _drawDot: function(ctx, rx, ry) {
      ctx.beginPath();
      ctx.arc(rx * 0.5 * this.width, ry * 0.5 * this.height, 3, 0, Math.PI * 2, false);
      return ctx.fill();
    }
  });

}).call(this);
