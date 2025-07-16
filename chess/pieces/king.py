from math import copysign
from typing import Literal
from chess.boards.board import Board
from chess.movement.movement import Movement
from chess.players._player import Player
from chess.pieces._piece import WithMovementObserver
from chess.position import Position
from chess.pieces.rook import Rook


class King(WithMovementObserver):
    DEFAULT_REPRESENTATION = ("♔", "♚")
    CHECKMATE_REPRESENTATION = ("🨳", "🨹")
    REPRESENTATION = DEFAULT_REPRESENTATION

    NOTATION = 'k'

    def __init__(self, board: Board, player: Player, x: str, y: int | None = None) -> None:
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

    @property
    def king_casteling_rook(self) -> Rook | None:
        return self.board.pieces.of(self.player).where(
            lambda p: isinstance(p, Rook) and not p.has_moved
        ).at(
            Position.valid_board_x[-1] + self.position.y
        ).first()  # type: ignore

    @property
    def queen_casteling_rook(self) -> Rook | None:
        return self.board.pieces.of(self.player).where(
            lambda p: isinstance(p, Rook) and not p.has_moved
        ).at(
            Position.valid_board_x[0] + self.position.y
        ).first()  # type: ignore

    def __able_to_castle_for(self, movement: Movement) -> bool:
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

    def legal_movements(self, board: Board) -> list[Movement]:
        allowed_casteling = []
        # Casteling
        if not self.has_moved:
            if self.king_casteling_rook is not None:
                movement = self.castle_movement('king')
                if self.__able_to_castle_for(movement):
                    allowed_casteling.append(movement)
            if self.queen_casteling_rook is not None:
                movement = self.castle_movement('queen')
                if self.__able_to_castle_for(movement):
                    allowed_casteling.append(movement)

        return super().legal_movements(board) + allowed_casteling

    @staticmethod
    def castle_type(movement: Movement):
        x_shift, y_shift = movement.difference
        if abs(x_shift) == 2 and y_shift == 0:
            return 'king' if x_shift > 0 else 'queen'

    def castle_movement(self, castle_type: Literal['king', 'queen'], with_rook_cascade: bool = True):
        direction = -1 if castle_type == 'queen' else 1

        king_movement = self.position.move().addX(2, direction).get()
        if with_rook_cascade is False:
            return king_movement
        rook = self.king_casteling_rook if castle_type == 'king' else self.queen_casteling_rook
        assert rook is not None, "Cannot get the castle movement with rook as the rook does not exists."

        return king_movement.cascading(
            Movement(
                rook.position,
                king_movement.to_position.move().addX(-1, direction).get().to_position
            )
        )

    def is_check(self):
        return self.board.pieces.of(self.player, False).contesting(self.position).exist()

    def is_check_mate(self, board: 'Board'):
        for piece in self.board.pieces.of(self.player):
            if piece.legal_movements(board):
                return False
        return True
