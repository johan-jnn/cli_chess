from typing import Any, Literal
from chess.board import Board
from chess.movement.movement import Movement
from chess.pieces._piece import Piece
from chess.pieces.bishop import Bishop
from chess.pieces.knight import Knight
from chess.pieces.queen import Queen
from chess.pieces.rook import Rook
from chess.players._player import Player
from chess.position import Position


class Pawn(Piece):
    REPRESENTATION = ("♙", "♟")
    NOTATION = 'p'

    PROMOTABLE_AS: list[tuple[str, Any]] = [
        ('reine', Queen),
        ('tour', Rook),
        ('cavalier', Knight),
        ('fou', Bishop)
    ]

    def __init__(self, board: Board, player: Player, x: str, y: int | None = None) -> None:
        super().__init__(board, player, 1, x, y)
        self.__moved = False
        self.promoted_as: Piece | None = None
        self.__force_promotion_to: Any | None = None
        self.__init_position = str(self.position)

    def will_promote_as(self, choice: type[Piece] | Literal['ask']):
        if choice == "ask":
            self.__force_promotion_to = None
        else:
            assert choice in [valid[1] for valid in self.PROMOTABLE_AS]
            self.__force_promotion_to = choice

        return self

    @property
    def promotion_forced_to(self):
        return self.__force_promotion_to or 'ask'

    @property
    def playable(self):
        return super().playable and self.promoted_as is None

    def require_promotion(self, movement: Movement):
        return (
            self.promoted_as is None
            and movement.to_position.raw_y in (Position.valid_board_y[0], Position.valid_board_y[-1])
        )

    def __promote(self):
        if self.__force_promotion_to is not None:
            self.promoted_as = self.__force_promotion_to(
                self.board, self.player, str(self.position)
            )
            return

        print("Le pion est promu !")
        while not self.promoted_as:
            promote_as = input(
                "Choisissez une pièce ('r' | 't' | 'c' | 'f'): "
            ).lower()
            for (name, piece) in self.PROMOTABLE_AS:
                if name.startswith(promote_as):
                    self.promoted_as = piece(
                        self.board, self.player, str(self.position)
                    )
                    return
            print("Veuillez choisir une pièce valide !")

    def moved(self, movement: Movement) -> None:
        self.__moved = True
        if self.require_promotion(movement):
            # Temporary ghost the piece to avoid the "existing piece at this position" error
            self.ghost = True
            self.__promote()
            self.ghost = False

        return super().moved(movement)

    def unmoved(self, movement: Movement) -> None:
        if self.promoted_as:
            self.promoted_as.remove_from_board()
            self.promoted_as = None

        if str(movement.from_position) == self.__init_position:
            self.__moved = False

        return super().unmoved(movement)

    def possible_movements(self) -> list[Movement]:
        moves = []
        forward = self.position.move().addY(1, self.player.direction).safe_get()
        if forward and not self.board.pieces.at(forward.to_position).exist():
            moves.append(forward)

        # The "and moves" is to verify there is no piece in front of this one
        if not self.__moved and moves:
            forward2 = self.position.move().addY(2, self.player.direction).safe_get()
            if forward2 and not self.board.pieces.at(forward2.to_position).exist():
                moves.append(forward2)

        for x in -1, 1:
            move = self.position.move().addXY(x, 1, self.player.direction).safe_get()
            if move is None:
                continue
            if self.board.pieces.at(move.to_position).of(self.player, False).exist():
                moves.append(move)

        return moves
