#---------------------------------------------------------------------------
# Dominoes Bone aka Tile
#---------------------------------------------------------------------------

radiansToDegrees = fabric.util.radiansToDegrees

Bone = fabric.util.createClass fabric.Rect,
    type:             "bone"
    left:             100
    top:              100
    width:            53
    height:           28
    stroke:           "#656565"
    fill:             "#d0d0d0"
    hasControls:      false
    hasBorders:       false
    originX:          "center"
    originY:          "center"
    lockMovementX:    true
    lockMovementY:    true
    isMoveable:       false

    initialize: (options={}) ->
        @callSuper("initialize", options)
        @leftDots  = options.leftDots
        @rightDots = options.rightDots
        @origPos   = new fabric.Point(@left, @top)
        @amMoving  = false
        return

    dragTo: (op) ->
        if @isMoveable
            dragged = @game.area.getPointer(op.e)
            @moveTo(dragged)
            @game.session.publish("dominoes:move", [dragged])
        return

    endDrag: ->
        if @isMoveable
            @reset()
            @game.session.publish("dominoes:drop")
        return

    recvMove: (args) ->
        @moveTo(args[0])
        @game.area.renderAll()
        return

    recvDrop: (args) ->
        @reset()
        return

    moveTo: (dragged) ->
        center = @getCenterPoint()
        if not @amMoving
            @amMoving = true
            if dragged.x < center.x
                @clickedLeft = true
            @game.area.bringToFront(@)
            @setShadow("4px 4px 8px rgba(0,0,0,0.2)")
        if dragged.x < @width/2
            dragged.x = @width/2
        if dragged.x > @game.area.width - @width/2
            dragged.x = @game.area.width - @width/2
        if dragged.y < @width/2
            dragged.y = @width/2
        if dragged.y > @game.area.height - @width/2
            dragged.y = @game.area.height - @width/2
        angle  = Math.atan2(dragged.x - center.x, center.y - dragged.y)
        if @clickedLeft
            angle += Math.PI/2
            @left = dragged.x + Math.cos(angle) * @width/4
            @top  = dragged.y + Math.sin(angle) * @width/4
        else
            angle -= Math.PI/2
            @left = dragged.x - Math.cos(-angle) * @width/4
            @top  = dragged.y + Math.sin(-angle) * @width/4
        @angle = radiansToDegrees(angle)
        return

    attachesTo: (other) ->
        return false

    reset: ->
        center = @getCenterPoint()
        angle = Math.atan2(center.x - @origPos.x, @origPos.y - center.y)
        if @clickedLeft
            angle += Math.PI/2
        else
            angle -= Math.PI/2
        @animate "angle", radiansToDegrees(angle),
            duration:   50,
            onChange: => @game.area.renderAll()
            onComplete: =>
                if @angle < -180
                    finalAngle = -360
                else if @angle > 180
                    finalAngle = 360
                else
                    finalAngle = 0
                props =
                    "left":   @origPos.x
                    "top":    @origPos.y
                    "angle":  finalAngle
                animation =
                    duration:   120,
                    onChange:   @game.area.renderAll.bind(@game.area)
                    onComplete: =>
                        @setShadow(null)
                        @game.area.sendToBack(@)
                        @game.area.renderAll()
                        @clickedLeft  = false
                        @amMoving     = false
                        @angle        = 0
                        return
                @animate(props, animation)
                return
        return

    _render: (ctx) ->
        @callSuper("_render", ctx)
        ctx.save()
        ctx.translate(-@width/4, 0)
        @_drawDots(ctx, @leftDots)
        ctx.translate(@width/2, 0)
        @_drawDots(ctx, @rightDots)
        ctx.restore()
        return

    _drawDots: (ctx, numDots) ->
        switch numDots
            when 0 then break
            when 1
                ctx.fillStyle = "#088587"
                @_drawDot(ctx,  0,     0)
            when 2
                ctx.fillStyle = "#21a603"
                @_drawDot(ctx, -0.25, -0.5)
                @_drawDot(ctx,  0.25,  0.5)
            when 3
                ctx.fillStyle = "#ff636e"
                @_drawDot(ctx, -0.25, -0.5)
                @_drawDot(ctx,  0,     0)
                @_drawDot(ctx,  0.25,  0.5)
            when 4
                ctx.fillStyle = "#ab593d"
                @_drawDot(ctx, -0.25, -0.5)
                @_drawDot(ctx,  0.25, -0.5)
                @_drawDot(ctx, -0.25,  0.5)
                @_drawDot(ctx,  0.25,  0.5)
            when 5
                ctx.fillStyle = "#0863bf"
                @_drawDot(ctx, -0.25, -0.5)
                @_drawDot(ctx,  0.25, -0.5)
                @_drawDot(ctx,  0,     0)
                @_drawDot(ctx, -0.25,  0.5)
                @_drawDot(ctx,  0.25,  0.5)
            when 6
                ctx.fillStyle = "#ffb31a"
                @_drawDot(ctx, -0.33, -0.5)
                @_drawDot(ctx,  0,    -0.5)
                @_drawDot(ctx,  0.33, -0.5)
                @_drawDot(ctx, -0.33,  0.5)
                @_drawDot(ctx,  0,     0.5)
                @_drawDot(ctx,  0.33,  0.5)
            when 7
                ctx.fillStyle = "#d5288f"
                @_drawDot(ctx, -0.33, -0.52)
                @_drawDot(ctx,  0,    -0.52)
                @_drawDot(ctx,  0.33, -0.52)
                @_drawDot(ctx,  0,     0)
                @_drawDot(ctx, -0.33,  0.52)
                @_drawDot(ctx,  0,     0.52)
                @_drawDot(ctx,  0.33,  0.52)
            when 8
                ctx.fillStyle = "#0b928c"
                @_drawDot(ctx, -0.33, -0.52)
                @_drawDot(ctx,  0,    -0.52)
                @_drawDot(ctx,  0.33, -0.52)
                @_drawDot(ctx, -0.33,  0)
                @_drawDot(ctx,  0.33,  0)
                @_drawDot(ctx, -0.33,  0.52)
                @_drawDot(ctx,  0,     0.52)
                @_drawDot(ctx,  0.33,  0.52)
            when 9
                ctx.fillStyle = "#5b2d55"
                @_drawDot(ctx, -0.33, -0.52)
                @_drawDot(ctx,  0,    -0.52)
                @_drawDot(ctx,  0.33, -0.52)
                @_drawDot(ctx, -0.33,  0)
                @_drawDot(ctx,  0,     0)
                @_drawDot(ctx,  0.33,  0)
                @_drawDot(ctx, -0.33,  0.52)
                @_drawDot(ctx,  0,     0.52)
                @_drawDot(ctx,  0.33,  0.52)
            when 10
                ctx.fillStyle = "#f79035"
                @_drawDot(ctx, -0.34,  -0.55)
                @_drawDot(ctx, -0.116, -0.55)
                @_drawDot(ctx,  0.116, -0.55)
                @_drawDot(ctx,  0.34,  -0.55)
                @_drawDot(ctx, -0.34,   0)
                @_drawDot(ctx,  0.34,   0)
                @_drawDot(ctx, -0.34,   0.55)
                @_drawDot(ctx, -0.116,  0.55)
                @_drawDot(ctx,  0.116,  0.55)
                @_drawDot(ctx,  0.34,   0.55)
            when 11
                ctx.fillStyle = "#641223"
                @_drawDot(ctx, -0.34,  -0.55)
                @_drawDot(ctx, -0.116, -0.55)
                @_drawDot(ctx,  0.116, -0.55)
                @_drawDot(ctx,  0.34,  -0.55)
                @_drawDot(ctx, -0.34,   0)
                @_drawDot(ctx,  0,      0)
                @_drawDot(ctx,  0.34,   0)
                @_drawDot(ctx, -0.34,   0.55)
                @_drawDot(ctx, -0.116,  0.55)
                @_drawDot(ctx,  0.116,  0.55)
                @_drawDot(ctx,  0.34,   0.55)
            when 12
                ctx.fillStyle = "#cc6663"
                @_drawDot(ctx, -0.34,  -0.55)
                @_drawDot(ctx, -0.116, -0.55)
                @_drawDot(ctx,  0.116, -0.55)
                @_drawDot(ctx,  0.34,  -0.55)
                @_drawDot(ctx, -0.34,   0)
                @_drawDot(ctx, -0.116,  0)
                @_drawDot(ctx,  0.116,  0)
                @_drawDot(ctx,  0.34,   0)
                @_drawDot(ctx, -0.34,   0.55)
                @_drawDot(ctx, -0.116,  0.55)
                @_drawDot(ctx,  0.116,  0.55)
                @_drawDot(ctx,  0.34,   0.55)
        return

    _drawDot: (ctx, rx, ry) ->
        ctx.beginPath()
        ctx.arc(rx * 0.5 * @width, ry * 0.5 * @height,
                3, 0, Math.PI * 2, false)
        ctx.fill()

