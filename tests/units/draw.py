from chess.boards.board import Board
from chess.pieces.bishop import Bishop
from chess.pieces.king import King
from chess.players.physical import PhysicalPlayer


board = Board()
whites = PhysicalPlayer(1)
blacks = PhysicalPlayer(-1)

King(board, whites, "f7")
King(board, blacks, "h7")

Bishop(board, whites, "g7")

verifier = blacks.verify_status(board).verify_for_check().verify_for_end_game()
assert verifier.is_draw and not verifier.is_check_mate
