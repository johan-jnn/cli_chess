from chess.game.game import ChessGame
from chess.players._player import Player
from chess.players.physical import PhysicalPlayer


def units():
    import tests.units.check
    import tests.units.check_mate
    import tests.units.draw


def debug():
    game = ChessGame((
        PhysicalPlayer(Player.WHITES_DIRECTION, "Whites"),
        PhysicalPlayer(Player.BLACKS_DIRECTION, "Blacks")
    ))
    game.start()
    game.autoplay()
