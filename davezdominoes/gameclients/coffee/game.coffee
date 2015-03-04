#---------------------------------------------------------------------------
# Dominoes Game
#---------------------------------------------------------------------------

class Run
    constructor: (@game, startBoneId) ->
        dots = startBoneId.split("|")
        bone = new Bone
            game:      @game
            left:      400
            top:       250
            leftDots:  parseInt(dots[0])
            rightDots: parseInt(dots[1])
        @bones         = [bone]
        @insideBone    = bone
        @outsideBone   = bone
        @game.area.add(bone)
        return

class Hand
    constructor: (@game) ->
        @bones = []

    draw: (boneIds) ->
        for boneId, i in boneIds
            dots = boneId.split("|")
            bone = new Bone
                game:      @game
                left:       100 + i * 60
                top:        450
                leftDots:   parseInt(dots[0])
                rightDots:  parseInt(dots[1])
                isMoveable: true
            bone.left = 800
            bone.top  = 0
            @game.area.add(bone)
            @bones.push(bone)
        for bone in @bones
            bone.reset()
        return

class Dominoes.Game
    constructor: (@gameId) ->
        console.log("new Game #{@gameId}")
        @area = new PlayingArea "playing-area",
            game:      @
            width:     800
            height:    500
            selection: false
        @hand = undefined
        @run  = undefined
        @my   = {}

        #boneBg = "/static/img/marblebg.png"
        boneBg = false
        if boneBg
            fabric.util.loadImage boneBg, (img) =>
                if img
                    Bone::fill = new fabric.Pattern
                        source:  img
                        offsetX: 26
                        offsetY: 14
                    @area.renderAll()

    connect: ->
        conn = new autobahn.Connection
            url:         Dominoes.url
            realm:       "game"+@gameId
            authmethods: ["beaker"]

        conn.onopen = (@session) =>
            console.log("Connected to #{Dominoes.url}")
            @session.prefix("dominoes", "nz.net.software.dominoes")
            @session.subscribe("dominoes:update", @onUpdate.bind(@))
            @session.call("dominoes:ready").then(@inGame.bind(@))
        conn.open()

    inGame: (retval) ->
        console.log("begin play")
        kwargs = retval.kwargs
        [@my.login, @my.name, @my.avatarUrl, bones] = kwargs.player
        @hand = new Hand(@)
        @hand.draw(bones)
        ######for player in kwargs.players
        ##########no other players in solitaire
        @run = new Run(@, kwargs.start)
        return

    onUpdate: (args, kwargs, dtl) ->
        return


Dominoes.play = (gameId) ->
    game = new Dominoes.Game(gameId)
    game.connect()
    return

