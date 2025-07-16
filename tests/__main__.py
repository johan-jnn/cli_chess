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


def units():
    import tests.units.check
    import tests.units.check_mate
    import tests.units.draw


def debug():
    units()
