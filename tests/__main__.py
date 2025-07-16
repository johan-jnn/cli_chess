from copy import copy
from chess import position
from chess.boards.board import Board
from chess.game.game import ChessGame
from chess.movement.board_movement import BoardMovement
from chess.movement.movement import Movement
from chess.pieces.bishop import Bishop
from chess.pieces.king import King
from chess.pieces.pawn import Pawn
from chess.pieces.queen import Queen
from chess.pieces.rook import Rook
from chess.players.physical import PhysicalPlayer
from chess.position import Position


def debug():
    # board = Board()
    whites = PhysicalPlayer(1)
    blacks = PhysicalPlayer(-1)

    # King(board, whites, 'e1')
    # King(board, blacks, 'd8')

    # Rook(board, whites, 'a1')
    # Rook(board, whites, 'h1')

    # # Bishop(board, blacks, 'd3')

    # # Pawn(board, whites, 'a2')

    # game = ChessGame((whites, blacks), board)
    # game.debug = True
    # game.start()

    # # game.exec_move(BoardMovement.decode('0-0', board, game.now_playing()))
    # game.play('0-0')
    # game.moves.manage_last().undo()  # type:ignore
    # game.play('0-0')
    # game.autoplay()
    game = ChessGame((whites, blacks)).start()
    game.play("nh3")
    game.play("e5")
    game.play("e3")
    game.play("g6")
    game.play("b5")
    game.play("h5")

    game.autoplay()
    #! Move: kg1 -> rook isn't moving.
