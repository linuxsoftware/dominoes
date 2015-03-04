# ------------------------------------------------------------------------------
# Game Rules
# ------------------------------------------------------------------------------

import sys
from abc import ABCMeta, abstractmethod

import logging
log = logging.getLogger(__name__)

# ------------------------------------------------------------------------------
# Game Rules base class
# ------------------------------------------------------------------------------
class GameRules(metaclass = ABCMeta):
    minPlayers = 2
    maxPlayers = 4

    @property
    @abstractmethod
    def name():
        """rule name"""

    @property
    @abstractmethod
    def instructions():
        """instructions on how to play"""

    def __str__(self):
        return self.name

# ------------------------------------------------------------------------------
# Block aka Straight Dominoes
# ------------------------------------------------------------------------------
# from http://www.domino-games.com/domino-rules/block-dominoes-rules.html
class BlockGameRules(GameRules):
    name = "Block Game"
    instructions = """
Block Dominoes, also known as The Block Game, is the simplest of all domino
games, and among the most familiar. As such is the forerunner of most other
domino games.

After shuffling the dominoes, each player draws tiles to make up their hand.
The number of tiles drawn depends on the number of players:

2 players draw 7 tiles each, 3 players draw 5 tiles each, 4 players draw 5
tiles each.  The remainder of the tiles in the boneyard are not used. If there
are four players, then they may play as partners, with the partners normally
sitting across from each other.

The player with the highest double places the first domino. Play proceeds to
the left (clockwise). Each player adds a domino to an open end of the layout,
if he can. In the illustration to the right, for instance, the game is well in
progress, and the "blank" and "1" are the open ends. Note that the layout may
flow in any direction, turning as necessary. Note also that the 5-5 and 1-1 are
placed in the customary crossways orientation, though may just as properly be
placed in an inline orientation.

A player that cannot make a move must pass. In the block game, players may not
draw tiles from the boneyard. The game ends when one player uses the last
domino in his hand, or when no more plays can be made. If all players still
have tiles in their hand, but can more no moves can be made, then the game is
said to be "blocked".

The player with the lightest hand (i.e. the number of dots on their dominoes)
wins the number of sum total of points in all of his opponents hands, minus the
points in his own hand. If there is a tie, the win goes to the player with the
lightest individual tile. For example, if one player has a 1-2, 2-4, and 3-5,
and the other player has a 5-5 and a 3-4, they both have a total of 17, but the
first player wins because his lightest tile (1-2) is smaller than the second
player's lightest tile (3-4).

Games are often played in a number of rounds, where the score in each
individual round (or hand) is added to the score in the previous rounds. When
one player's total score exceeds a pre-established "winning score" (100, for
example), the game is over and the winner declared.
"""

# ------------------------------------------------------------------------------
# Draw Dominoes
# ------------------------------------------------------------------------------
class DrawGameRules(GameRules):
    name = "Draw Game"
    instructions = """
Draw Dominoes, also known as The Draw Game, is one of the simpler domino games, and among the most popular as well.

After shuffling the dominoes, each player draws tiles to make up their hand. The number of tiles drawn depends on the number of players:

2 players draw 7 tiles each, 3 players draw 5 tiles each, 4 players draw 5
tiles each.  The remainder of the tiles make up the boneyard (or "stock"), and
are held in or reserve to be drawn upon at need.

The player with the highest double places the first domino. Play proceeds to
the left (clockwise). Each player adds a domino to an open end of the layout,
if he can. In the illustration to the right, for instance, the game is well in
progress, and the "blank" and "1" are the open ends. Note that the layout may
flow in any direction, turning as necessary. Note also that the 5-5 and 1-1 are
placed in the customary crossways orientation, though may just as properly be
placed in an inline orientation.

If a player is unable to make a move, he must draw dominoes from the boneyard
until he can make a move. If there are no dominoes left, then the player must
pass.

A game ends either when a player plays all his tiles, or when a game is
blocked. A game is blocked when no player is able to add another tile to the
layout.

When a hand ends, the player with the lightest hand (i.e. the fewest number of
dots on their dominoes) wins the number of sum total of points in all of his
opponents hands (minus the points in his own hand, if any).

A game of Draw Dominoes is typically played to a score of 100.
"""

# ------------------------------------------------------------------------------
# Solitaire Dominoes
# ------------------------------------------------------------------------------
# from http://www.ehow.com/how_8685550_play-solitaire-dominoes.html
class SolitaireRules(GameRules):
    minPlayers = 1
    maxPlayers = 1
    numBonesToDraw = 5
    name = "Solitaire"
    instructions = """
Place all of the dominoes face down on the tabletop and shuffle them.

Select one domino and flip it over; this is the starter domino. Push aside
the rest of the dominoes, leaving them face down.

Select five dominoes.

Place the dominoes in your hand, building off of the starter as you would if
playing a multi-player game. Select a domino that has a number in common with
the starter domino. Set the domino down on the board so that the common numbers
touch, either vertically or horizontally.

Continue to place dominoes until all of the dominoes in your hand are used.

Draw five more dominoes and place them on the board in the same manner.

Repeat, drawing five dominoes at a time and placing them until you have used
all of the dominoes. If you get stuck and find that you cannot place another
domino, you lose the game.
"""

# ------------------------------------------------------------------------------
# Mexican Trains
# ------------------------------------------------------------------------------
class MexicanTrainsRules(GameRules):
    name = "Mexican Trains"
    # TODO find better instructions?
    instructions = """
Domino Trains is a simple game, which can utilize any of the five domino sets,
although the larger sets significantly increase the length of the game. The
basic gist of Trains is the player must match his/her dominos in numeric
sequence. The object of the game is to have as few points as possible at the
end of each round.

The Deal and Starting Out: The game starts with the highest or lowest double of
the set, and then each hand after goes either up or down (18 would be followed
by 17, then 16; blanks would be followed by 1s, then 2s, etc),. This is placed
in the middle of the playing area. Then, the players draw the agreed upon
amount of dominos from the boneyard. For four players and under, the convention
is to draw a domino for each denomination. In Double 9s, 10 dominos would be
drawn; in double 12s, 13 would be drawn; double 15s, 16 would be drawn, and
double 18s, 19 would be drawn. However, the total number drawn can be varied to
suit the players. On the first hand, the first player is determined by who has
the highest value single domino in that hand.

Basic Gameplay: Each player begins his/her own private train off of the lead
double in the central playing area. Players then must match up his/her dominos
to follow a train, with the lead tile of the train matching whatever double is
currently being used. The order of play goes in either clockwise or
counterclockwise order, depending on the preference of the players, with the
players laying down one domino per turn, save in the case of doubles, when it
is two tiles.

If a person cannot play on his/her own private train, he must draw one domino
from the boneyard; if, after drawing from the boneyard is still unable to play,
s/he must place a marker (generally coins) on his/her private train, marking
that the train is now open for anyone to play upon. Until the player can play,
s/he must continue to draw one domino each time it is his/her turn. Once the
player draws the required domino to enable him/her to resume play on his
private train and plays it, if s/he does not take the marker off by the end of
his/her turn, indicating the train is no longer available for general play by
anyone, the train must remain open until the player’s next turn, whereby s/he
can remove the marker.

When a player plays a double, s/he must follow the double with an additional
tile that follows the tile. If a player plays a double on his own train, then
he doesn't have obligation to statisfy the double. Instead, he can play another
tile on mexican train if he has matching tile. The next player will have
obligation to satisfy that double. If a player plays a double and does not have
an additional tile to match the double s/he played, s/he must draw a domino
from the boneyard. If, after drawing from the boneyard, the player is still
unable to play on the double s/he just laid down, s/he cannot lay any
additional tiles down on any open trains, even if there is an available play.
The only time two dominos may be laid down in a single play is a double and a
corresponding tile to that double. A possible exception to this rule is, if
after playing a double and unable to follow the double up with an appropriately
numbered domino and drawing, if the player has another double that is available
for play s/he may lay that down; however, s/he must follow that double up as
well, and if s/he cannot s/he must draw.

Others play that if a double is played and the person cannot finish the play,
all other plays are suspended for all players, and it is the responsibility of
the next player to finish the already played double. If the next player cannot
play on the double, s/he must draw, and if s/he does not get a possible play,
then the subsequent player must attempt to play on the double, and so on, until
the double has been satisfied.

Scoring and Round Completion: The round is finished when a player runs out of
dominos and can no longer play. Afterward, the remaining domino’s pips in the
other players’ hands are counted as points. If no player can go out, the
remainder in each person’s hand is count, and who ever has the fewest points
leads the next round. This cycle is continued until the players go through the
full domino set, and whoever has the least points wins the game.
"""


# ------------------------------------------------------------------------------
