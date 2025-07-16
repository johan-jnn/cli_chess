from chess.boards.board import Board
from chess.movement.movement import Movement
from chess.pieces._piece import Piece
from chess.players._player import Player


class Knight(Piece):
    REPRESENTATION = ("♘", "♞")
    NOTATION = 'n'

    def __init__(self, board: Board, player: Player, x: str, y: int | None = None) -> None:
        super().__init__(board, player, 3, x, y)

    def possible_movements(self) -> list[Movement]:
        moves = []

        for dx in range(-2, 3):
            for dy in range(-2, 3):
                if abs(dx) == abs(dy) or not (dx and dy):
                    continue
                move = self.position.move().addXY(dx, dy).safe_get()
                if not move:
                    continue

                if (
                    self.board.pieces.at(move.to_position).of(
                        self.player
                    ).exist()
                ):
                    continue
                moves.append(move)
        return moves
