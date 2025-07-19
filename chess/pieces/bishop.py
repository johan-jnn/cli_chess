from typing import TYPE_CHECKING
from chess.movement.movement import Movement
from chess.pieces._piece import Piece
from chess.players._player import Player

if TYPE_CHECKING:
    from chess.boards.board import Board


class Bishop(Piece):
    REPRESENTATION = ("♗", "♝")
    NOTATION = 'b'

    def __init__(self, board: 'Board', player: Player, x: str, y: int | None = None) -> None:
        super().__init__(board, player, 3, x, y)

    def contesting_positions(self) -> list[Movement]:
        contesting = []

        for dx in [-1, 1]:
            for dy in [-1, 1]:
                distance = 1
                while 1:
                    position = self.position.move().addXY(dx, dy, distance).safe_position()
                    if not position:
                        break

                    override_piece = self.board.pieces.at(position).first()
                    if override_piece:
                        if override_piece.player is not self.player:
                            contesting.append(position)
                        break
                    contesting.append(position)
                    distance += 1

        return contesting
