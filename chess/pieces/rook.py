from chess.boards.board import Board
from chess.movement.movement import Movement
from chess.pieces._piece import WithMovementObserver
from chess.players._player import Player


class Rook(WithMovementObserver):
    REPRESENTATION = ("♖", "♜")
    NOTATION = 'r'

    def __init__(self, board: Board, player: Player, x: str, y: int | None = None) -> None:
        super().__init__(board, player, 5, x, y)

    def possible_movements(self) -> list[Movement]:
        moves = []

        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if dx and dy:
                    continue

                distance = 1
                while 1:
                    move = self.position.move().addXY(dx, dy, distance).safe_get()
                    if not move:
                        break

                    override_piece = self.board.pieces.at(
                        move.to_position).first()
                    if override_piece:
                        if override_piece.player is not self.player:
                            moves.append(move)
                        break
                    moves.append(move)
                    distance += 1
        return moves
