#---------------------------------------------------------------------------
# Dominoes namespace
#---------------------------------------------------------------------------

@Dominoes =
    login: ""

    initialize: (options={}) ->
        $.extend(@, options)
        @host    ?= "127.0.0.1"
        @port    ?= 9000
        @encrypt ?= false
        @scheme  ?= if @encrypt then "wss" else "ws"
        @url = "#{@scheme}://#{@host}:#{@port}"
        console.log("Dominoes GameServer @ #{@url}")

