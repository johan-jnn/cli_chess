from copy import copy
from chess import position
from chess.board import Board
from chess.game.game import ChessGame
from chess.movement.movement import Movement
from chess.pieces.king import King
from chess.pieces.pawn import Pawn
from chess.pieces.queen import Queen
from chess.pieces.rook import Rook
from chess.players.physical import PhysicalPlayer
from chess.position import Position


def debug():
    board = Board()
    whites = PhysicalPlayer(1, "Whites")
    blacks = PhysicalPlayer(-1, "Blacks")

    King(board, whites, 'd6')
    King(board, blacks, 'd8')

    # Rook(board, whites, 'h1')
    # Rook(board, whites, 'h6')
    
    Pawn(board, whites, 'h7')

    game = ChessGame((whites, blacks), board)
    game.debug = True
    game.start().autoplay()
