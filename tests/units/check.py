from chess.boards.board import Board
from chess.pieces.king import King
from chess.pieces.rook import Rook
from chess.players.physical import PhysicalPlayer


board = Board()
whites = PhysicalPlayer(1)
blacks = PhysicalPlayer(-1)

King(board, whites, "a1")
King(board, blacks, "h1")

Rook(board, whites, "h4")

verifier = blacks.verify_status(board).verify_for_check().verify_for_end_game()
assert verifier.is_checked and not verifier.is_check_mate
