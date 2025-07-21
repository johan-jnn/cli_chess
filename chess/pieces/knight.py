from typing import TYPE_CHECKING
from chess.pieces._piece import Piece
from chess.players._player import Player
from chess.position import Position

if TYPE_CHECKING:
    from chess.boards.board import Board


class Knight(Piece):
    REPRESENTATION = ("♘", "♞")
    NOTATION = 'n'

    def __init__(self, board: 'Board', player: Player, x: str, y: int | None = None) -> None:
        super().__init__(board, player, 3, x, y)

    def contesting_positions(self) -> list[Position]:
        contesting = []

        for dx in range(-2, 3):
            for dy in range(-2, 3):
                if abs(dx) == abs(dy) or not (dx and dy):
                    continue
                position = self.position.move().addXY(dx, dy).safe_position()
                if not position:
                    continue

                if (
                    self.board.pieces.at(position).of(
                        self.player
                    ).exist()
                ):
                    continue
                contesting.append(position)
        return contesting
