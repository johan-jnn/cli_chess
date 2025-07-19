from typing import TYPE_CHECKING, Any, Literal
from chess.movement.movement import Movement
from chess.pieces._piece import Piece, WithMovementObserver
from chess.pieces.bishop import Bishop
from chess.pieces.knight import Knight
from chess.pieces.queen import Queen
from chess.pieces.rook import Rook
from chess.players._player import Player
from chess.position import Position

if TYPE_CHECKING:
    from chess.boards.board import Board, BoardMovement


class Pawn(WithMovementObserver):
    REPRESENTATION = ("♙", "♟")
    NOTATION = 'p'

    PROMOTABLE_AS: list[tuple[str, Any]] = [
        ('reine', Queen),
        ('tour', Rook),
        ('cavalier', Knight),
        ('fou', Bishop)
    ]

    def __init__(self, board: 'Board', player: Player, x: str, y: int | None = None) -> None:
        super().__init__(board, player, 1, x, y)
        self.__force_promotion_to: Any | None = None

    def force_promotion_as(self, choice: type[Piece] | Literal['ask']):
        if choice == "ask":
            self.__force_promotion_to = None
        else:
            assert choice in [valid[1] for valid in self.PROMOTABLE_AS]
            self.__force_promotion_to = choice

        return self

    def require_promotion(self, movement: Movement):
        return (
            self.playable
            and movement.to_position.raw_y in (Position.valid_board_y[0], Position.valid_board_y[-1])
        )

    def __promote(self) -> Piece:
        if self.__force_promotion_to is not None:
            return self.__force_promotion_to(
                self.board, self.player, str(self.position)
            )

        print("Le pion est promu !")
        while 1:
            promote_as = input(
                "Choisissez une pièce ('r' | 't' | 'c' | 'f'): "
            ).lower()
            for (name, piece) in self.PROMOTABLE_AS:
                if name.startswith(promote_as):
                    return piece(
                        self.board, self.player, str(self.position)
                    )
            print("Veuillez choisir une pièce valide !")

        raise IndexError("The promotion has not been made.")

    def _is_movement_legal(self, movement: 'BoardMovement'):
        reset_promotion_to = self.__force_promotion_to
        self.force_promotion_as(self.PROMOTABLE_AS[0][1])

        is_legal = super()._is_movement_legal(movement)
        self.__force_promotion_to = reset_promotion_to

        return is_legal

    def moved(self, movement: Movement) -> None:
        super().moved(movement)

        if self.require_promotion(movement):
            movement.with_promotion = (self, self.__promote())
            self.ghost = True

    def move_canceled(self, movement: Movement) -> None:
        if movement.with_promotion:
            assert movement.with_promotion[0] is self, "Cannot unpromote: pieces are not the same."
            movement.with_promotion[1].remove_from_board()
            movement.with_promotion = None
            self.ghost = False

        return super().move_canceled(movement)

    def contesting_positions(self) -> list[Movement]:
        contesting = []
        forward = self.position.move().addY(1, self.player.direction).safe_position()
        if forward and not self.board.pieces.at(forward).exist():
            contesting.append(forward)

        # The "and contesting" is to verify there is no piece in front of this one
        if not self.has_moved and contesting:
            forward2 = self.position.move().addY(2, self.player.direction).safe_position()
            if forward2 and not self.board.pieces.at(forward2).exist():
                contesting.append(forward2)

        for x in -1, 1:
            position = self.position.move().addXY(x, 1, self.player.direction).safe_position()
            if position is None:
                continue
            if self.board.pieces.at(position).of(self.player, False).exist():
                contesting.append(position)

        return contesting
