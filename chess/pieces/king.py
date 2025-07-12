from typing import TYPE_CHECKING
from chess.board import Board
from chess.movement.movement import Movement
from chess.players._player import Player
from chess.pieces._piece import Piece

if TYPE_CHECKING:
    from chess.game.game import ChessGame


class King(Piece):
    REPRESENTATION = ("♔", "♚")
    NOTATION = 'k'

    def __init__(self, board: Board, player: Player, x: str, y: int | None = None) -> None:
        super().__init__(board, player, 999, x, y)

    def possible_movements(self) -> list[Movement]:
        moves = []

        for x in range(-1, 2):
            for y in range(-1, 2):
                if x == y == 0:
                    continue
                movement = self.position.move().addXY(x, y).safe_get()
                if movement:
                    override_piece = self.board.pieces.at(
                        movement.to_position).first()
                    if override_piece and override_piece.player is self.player:
                        continue

                    moves.append(movement)

        return moves

    def is_check(self):
        for piece in self.board.pieces.of(self.player, False):
            if self.position in [m.to_position for m in piece.possible_movements()]:
                return True
        return False

    def is_check_mate(self, board: 'Board'):
        for piece in self.board.pieces.of(self.player):
            if piece.legal_movements(board):
                return False
        return True
