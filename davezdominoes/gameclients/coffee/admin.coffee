class Dominoes.GameTablet
    constructor: (@myDiv, @gameId) ->
        myDivId = @myDiv.attr('id')
        console.log("new GameTablet #{@gameId} ##{myDivId}")

    connect: ->
        conn = new autobahn.Connection
            url:         Dominoes.url
            realm:       "game"+@gameId
            authmethods: ["beaker"]
        conn.onopen = (@session) =>
            console.log("Connected to #{Dominoes.url}")
            @session.prefix("dominoes", "nz.net.software.dominoes")
            @session.subscribe("dominoes:update", @onUpdate.bind(@))
            @myDiv.find(".join-game").click  => @session.call("dominoes:join")
            @myDiv.find(".leave-game").click => @session.call("dominoes:leave")
            @myDiv.find(".start-game").click => @session.call("dominoes:start")
            @session.call("dominoes:poke")
        conn.open()

    onUpdate: (args, kwargs, dtl) ->
        console.log("Got an update")
        @myDiv.find("span.status").text(kwargs.status)
        @myDiv.find("span.rules").text(kwargs.rules)
        playersList = @myDiv.find(".players")
        playersList.empty()
        for [login, name, avatar] in kwargs.players
            playerItem = $('<li>')
            avatar = $('<img src="'+avatar+'" alt="&nbsp;&nbsp;&nbsp;&nbsp;"
                             width="16" height="16"/>')
            playerItem.append(avatar)
            playerItem.append(' '+name+' ')
            if Dominoes.login == kwargs.players[0][0] and
               Dominoes.login != login
                kickLink = $(' <a href="javascript:void(0);"
                                  class="kick">Kick</a>')
                playerItem.append(kickLink)
            playersList.append(playerItem)

        @myDiv.find(".actions a").hide()
        if Dominoes.login in (player[0] for player in kwargs.players)
            @myDiv.addClass("playing")
            if kwargs.status == "Started"
                @myDiv.find(".play-game").show()
            else
                @myDiv.find(".leave-game").show()
        else
            @myDiv.removeClass("playing")
            @myDiv.find(".join-game").show()
            
        if kwargs.status == "Ready"
            if kwargs.players and kwargs.players[0][0] == Dominoes.login
                @myDiv.find(".start-game").show()
        return

Dominoes.admin = ->
    prefix = "game-tablet"
    $("div[id^='#{prefix}']").each ->
        gameId = $(@).attr('id').substr(prefix.length)
        tablet = new Dominoes.GameTablet($(@), gameId)
        $(@).data('dominoes_object', tablet)
        tablet.connect()
        return
    return
