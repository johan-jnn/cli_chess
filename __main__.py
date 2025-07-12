"""Main entry file"""

from sys import argv


if __name__ == "__main__":
    if "--test" in argv:
        from tests.__main__ import *
        debug()
    else:
        from chess.players.physical import PhysicalPlayer
        from chess.game.game import ChessGame
        whites = input("Nom des blancs: ")
        blacks = input("Nom des noirs: ")
        ChessGame((PhysicalPlayer(1, whites), PhysicalPlayer(-1, blacks))).start().autoplay()
