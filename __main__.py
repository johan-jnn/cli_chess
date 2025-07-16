"""Main entry file"""

from sys import argv
from tests.__main__ import debug, units


if __name__ == "__main__":
    if "--test" in argv:
        debug()
    elif "--units" in argv:
        units()
    else:
        from chess.players.physical import PhysicalPlayer
        from chess.game.game import ChessGame
        whites = input("Nom des blancs: ")
        blacks = input("Nom des noirs: ")
        ChessGame((PhysicalPlayer(1, whites),
                  PhysicalPlayer(-1, blacks))).start().autoplay()
