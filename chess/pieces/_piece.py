from shutil import move
from typing import TYPE_CHECKING, Callable, Literal
from chess.movement.movement import Movement
from chess.players._player import Player
from chess.position import Position
from chess.movement.board_movement import BoardMovement

if TYPE_CHECKING:
    from chess.boards.board import Board


class Piece:
    REPRESENTATION = (None, None)
    NOTATION = "!!UNDEFINED!!"

    def __init__(self, board: 'Board', player: Player, value: int, x: str, y: int | None = None) -> None:
        self.position = PiecePosition(self, x, y)
        assert not board.pieces.at(self.position).exist(
        ), "There is already a piece at this position on this board."

        self.eaten_by: Piece | None = None
        self.ghost = False
        self.value = value
        self.player = player
        self.board = board

        board._pieces.append(self)

    @property
    def playable(self):
        return not (self.eaten_by or self.ghost)

    def contesting_positions(self) -> list[Position]:
        """Get the list of the positions the piece is contesting
        """
        return []

    def _is_movement_legal(self, movement: 'BoardMovement'):
        if not (
            movement.board.pieces.at(movement.from_position).first() is self
        ):
            return False

        movement.validate(False)
        is_legal = not self.player.verify_status(
            movement.board
        ).with_check().is_checked
        movement.unvalidate()

        return is_legal

    def legal_movements(self):
        """Get the list of the piece's legals movements
        This method checks for:
            - All possible movements
            - checks
            - casteling

        Returns:
            list[Movement]
        """
        moves: list[Movement] = []
        for pos in self.contesting_positions():
            movement = BoardMovement((
                self.position,
                pos
            ), self.board)
            if self._is_movement_legal(movement):
                moves.append(movement)
        return moves

    def move(self, movement: Movement) -> None:
        from chess.pieces.king import King

        eaten = self.board.pieces.at(movement.to_position).first()
        if eaten is not None:
            assert eaten.player != self.player, "Cannot eat your own piece"
            assert not isinstance(eaten, King), "Cannot eat a king."
            eaten.eaten_by = self
            movement.with_piece_eaten = eaten

        self.position.copy_from(movement.to_position)
        return self.moved(movement)

    def moved(self, movement: Movement) -> None:
        """Should be executed after the piece has been moved by the given movement

        Args:
            movement (Movement): The movement the piece made
        """

    def cancel_move(self, movement: Movement) -> None:
        self.position.copy_from(movement.from_position)

        if movement.with_piece_eaten is not None:
            movement.with_piece_eaten.eaten_by = None
            movement.with_piece_eaten = None

        return self.move_canceled(movement)

    def move_canceled(self, movement: Movement) -> None:
        pass

    def remove_from_board(self):
        self.board._pieces.remove(self)

    def __str__(self) -> str:
        char = self.REPRESENTATION[self.player.is_black]
        return char if char else super().__str__()

# ----- PieceType helper


class WithMovementObserver(Piece):
    __moved_from: 'BoardMovement | None' = None

    @property
    def has_moved(self):
        return bool(self.__moved_from)

    def moved(self, movement: Movement) -> None:
        if self.__moved_from is None:
            self.__moved_from = movement.in_board(self.board)

        return super().moved(movement)

    def move_canceled(self, movement: Movement) -> None:
        if movement.in_board(self.board) is self.__moved_from:
            self.__moved_from = None

        return super().move_canceled(movement)

# ----- PieceList helper


class PieceList:
    def __init__(self, pieces: list[Piece]) -> None:
        self.__pieces = filter(None, pieces)

    def playable(self, is_playable: bool = True):
        self.__pieces = filter(
            lambda p: p.playable == is_playable,
            self.__pieces
        )
        return self

    def at(self, x: str | Position, y: int | None = None, should_be: bool = True):
        pos = x if isinstance(x, Position) else Position(x, y)

        self.__pieces = filter(
            lambda p: (p.position == pos) is should_be,
            self.__pieces
        )

        return self

    def of(self, player: Player, should_be: bool = True):
        self.__pieces = filter(
            lambda p: (p.player == player) is should_be,
            self.__pieces
        )

        return self

    def type(self, only: type[Piece], should_be: bool = True):
        self.__pieces = filter(
            lambda p: isinstance(p, only) is should_be,
            self.__pieces
        )

        return self

    def exept(self, *pieces: Piece):
        self.__pieces = filter(
            lambda p: p not in pieces,
            self.__pieces
        )

        return self

    def contesting(
            self,
            position: Position,
            and_can_move_to: bool = False,
            should_be: bool = True
    ):
        self.__pieces = filter(
            lambda p: (
                position in (
                    map(
                        lambda m: m.to_position,
                        p.legal_movements()
                    )
                    if and_can_move_to else p.contesting_positions()
                )
            ) == should_be,
            self.__pieces
        )

        return self

    def where(self, test: Callable[[Piece], bool], should_be: bool = True):
        self.__pieces = filter(
            lambda p: test(p) is should_be,
            self.__pieces
        )

        return self

    def get(self):
        return list(self.__pieces)

    def first(self):
        try:
            return next(self.__pieces)
        except StopIteration:
            return None

    def exist(self):
        return bool(self.first())

    def __iter__(self):
        return iter(self.__pieces)

    def __bool__(self):
        return self.exist()


class PiecePosition(Position):
    def __init__(self, piece: Piece, x: str, y: int | None = None) -> None:
        super().__init__(x, y)
        self.piece = piece
