from enum import Enum
from math import copysign
from typing import TYPE_CHECKING
from chess.movement.movement import Movement
from chess.pieces._piece import WithMovementObserver
from chess.position import Position
from chess.pieces.rook import Rook

if TYPE_CHECKING:
    from chess.players._player import Player
    from chess.boards.board import Board


class CastlingDirection(Enum):
    KING = 1
    QUEEN = -1


class King(WithMovementObserver):
    DEFAULT_REPRESENTATION = ("♔", "♚")
    CHECKMATE_REPRESENTATION = ("🨳", "🨹")
    REPRESENTATION = DEFAULT_REPRESENTATION

    NOTATION = 'k'

    def __init__(self, board: 'Board', player: 'Player', x: str, y: int | None = None) -> None:
        super().__init__(board, player, 0, x, y)

    def toggle_checkmate_representation(self, force: None | bool = None):
        use_check_mate = (
            self.REPRESENTATION == self.DEFAULT_REPRESENTATION
            if force is None
            else force
        )

        self.REPRESENTATION = (
            self.CHECKMATE_REPRESENTATION
            if use_check_mate
            else self.DEFAULT_REPRESENTATION
        )

        return self

    def contesting_positions(self) -> list[Movement]:
        contesting = []

        for x in range(-1, 2):
            for y in range(-1, 2):
                if x == y == 0:
                    continue
                if position := self.position.move().addXY(x, y).safe_position():
                    override_piece = self.board.pieces.at(position).first()

                    if override_piece and override_piece.player is self.player:
                        continue

                    contesting.append(position)

        return contesting

    def legal_movements(self) -> list[Movement]:
        castles = []

        for castle_direction in CastlingDirection:
            if movement := self.get_castle_movement(castle_direction):
                castles.append(movement)

        return super().legal_movements() + castles

    def moved(self, movement: Movement):
        movement.with_castling = self.castle_type(movement)
        super().moved(movement)

    def move_canceled(self, movement: Movement) -> None:
        movement.with_castling = None
        return super().move_canceled(movement)

    @staticmethod
    def castle_type(movement: Movement) -> CastlingDirection | None:
        x_shift, y_shift = movement.difference
        if abs(x_shift) == 2 and y_shift == 0:
            return CastlingDirection.KING if x_shift > 0 else CastlingDirection.QUEEN

    def __is_able_to_castle(self, movement: Movement) -> bool:
        """
        Tests if all cases in the king's movement are empty and not contested by a opponent's piece
        """
        if self.castle_type(movement) is None:
            return False

        # Checking if cases are not contested nor occupied
        start = movement.from_position.x_index
        end = movement.to_position.x_index
        direction = int(copysign(1, end - start))

        for x_index in range(start, end + 1 * direction, direction):
            position = Position(
                Position.valid_board_x[x_index], movement.from_position.raw_y
            )
            if (
                (self.position != position and self.board.pieces.at(position))
                or self.board.pieces.of(self.player, False).contesting(position)
            ):
                return False

        return True

    def get_castle_movement(self, direction: CastlingDirection) -> Movement | None:
        if self.has_moved:
            return

        king_movement = self.position.move().addX(2, direction.value).safe_movement()

        if not (king_movement and self.__is_able_to_castle(king_movement)):
            return

        rook_x_index = 0 if direction == CastlingDirection.QUEEN else -1
        rook: Rook | None = self.board.pieces.of(self.player).where(
            lambda p: isinstance(p, Rook) and not p.has_moved
        ).at(
            Position.valid_board_x[rook_x_index] + self.position.y
        ).first()  # type: ignore

        if rook is None:
            return

        rook_final_position = king_movement.to_position.move().addX(-1, direction.value).safe_position()
        if not rook_final_position:
            return

        return king_movement.cascading(
            rook.position.move().to(rook_final_position).movement()
        )
