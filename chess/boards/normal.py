from chess.boards.board import Board
from chess.pieces.bishop import Bishop
from chess.pieces.king import King
from chess.pieces.knight import Knight
from chess.pieces.pawn import Pawn
from chess.pieces.queen import Queen
from chess.pieces.rook import Rook
from chess.position import Position


class NormalBoard(Board):
    def setup(self, whites, blacks):
        self.empty()

        # Pawns
        for x_axis in Position.valid_board_x:
            for (white, pawn_y) in enumerate([7, 2]):
                Pawn(
                    self,
                    whites if white else blacks,
                    f"{x_axis}{pawn_y}"
                )
        # Rooks
        Rook(self, whites, "a1")
        Rook(self, whites, "h1")
        Rook(self, blacks, "a8")
        Rook(self, blacks, "h8")
        # Knight
        Knight(self, whites, "b1")
        Knight(self, whites, "g1")
        Knight(self, blacks, "b8")
        Knight(self, blacks, "g8")
        # Bishop
        Bishop(self, whites, "c1")
        Bishop(self, whites, "f1")
        Bishop(self, blacks, "c8")
        Bishop(self, blacks, "f8")

        queen_x = "e" if whites.is_black else "d"
        king_x = "e" if queen_x == "d" else "d"

        Queen(self, whites, f"{queen_x}1")
        Queen(self, blacks, f"{queen_x}8")

        King(self, whites, f"{king_x}1")
        King(self, blacks, f"{king_x}8")
