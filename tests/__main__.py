from chess.boards.board import Board
from chess.boards.normal import NormalEmptyBoard
from chess.boards.onedymention import OneDymentionBoard
from chess.game.game import ChessGame
from chess.pieces.king import King
from chess.pieces.knight import Knight
from chess.pieces.queen import Queen
from chess.players._player import Player
from chess.players.physical import PhysicalPlayer


def units():
    import tests.units.check
    import tests.units.check_mate
    import tests.units.draw


def debug():
    board = OneDymentionBoard()

    whites = PhysicalPlayer(Player.WHITES_DIRECTION, "Whites")
    blacks = PhysicalPlayer(Player.BLACKS_DIRECTION, "Blacks")

    # board.auto_setup_kings(
    #     (whites, "a1"),
    #     (blacks, "h1")
    # )

    # Queen(board, whites, "d5")

    game = ChessGame((whites, blacks), board)
    game.setup_board()
    game.start()
    game.autoplay()
