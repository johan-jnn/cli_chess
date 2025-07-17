from chess.boards.board import Board
from chess.pieces.bishop import Bishop
from chess.pieces.king import King
from chess.pieces.pawn import Pawn
from chess.players._player import DrawReason
from chess.players.physical import PhysicalPlayer


board = Board()
whites = PhysicalPlayer(1)
blacks = PhysicalPlayer(-1)

King(board, whites, "f7")
King(board, blacks, "h7")

Bishop(board, whites, "g7")

verifier = blacks.verify_status(board).with_draw()
assert verifier.is_draw and verifier.is_draw == DrawReason.INSUFFICIENT_MATERIAL

Pawn(board, whites, "a3")
Pawn(board, blacks, "a4")
verifier = blacks.verify_status(board).with_draw()

assert verifier.is_draw and verifier.is_draw == DrawReason.STALEMATE
