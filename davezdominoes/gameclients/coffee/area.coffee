#---------------------------------------------------------------------------
# Dominoes PlayingArea
#---------------------------------------------------------------------------

PlayingArea = fabric.util.createClass fabric.Canvas,
    initialize: (canvasId, options={}) ->
        @callSuper("initialize", canvasId, options)
        @selectedBone = null
        @game   = options.game
        @on("mouse:down", @onMouseDown)

    onMouseDown: (op) ->
        if op.target instanceof Bone and op.target.isMoveable
            @selectedBone = op.target
            @onMouseMove(op)
            @on("mouse:move", @onMouseMove)
            @on("mouse:up",   @onMouseUp)

    onMouseMove: (op) ->
        here = @getPointer(op.e)
        @selectedBone.moveTo(here)
        @game.session.publish("dominoes:move", [here])
        if @selectedBone.intersectsWithObject(@game.run.insideBone)
            @fooTouch(@selectedBone, @game.run.insideBone)

    fooTouch: (left, right) ->
        # TODO this is just a placeholder
        

        

    onMouseUp: (op) ->
        @selectedBone.reset()
        @game.session.publish("dominoes:drop")
        @selectedBone = null
        @off("mouse:move", @onMouseMove)
        @off("mouse:up",   @onMouseUp)

