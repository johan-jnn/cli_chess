from typing import TYPE_CHECKING, Callable, Literal
from chess.boards.board import Board
from chess.movement.movement import Movement
from chess.players._player import Player
from chess.position import Position

if TYPE_CHECKING:
    from chess.movement.board_movement import BoardMovement
    from chess.pieces.pawn import Pawn


class Piece:
    REPRESENTATION = (None, None)
    NOTATION = "!!UNDEFINED!!"

    def __init__(self, board: Board, player: Player, value: int, x: str, y: int | None = None) -> None:
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
    def promoted_from(self) -> 'Pawn|None':
        from chess.pieces.pawn import Pawn

        found = self.board.all_pieces.type(Pawn).where(
            lambda p: p.promoted_as is self  # type: ignore
        ).first()
        return found  # type: ignore

    @property
    def playable(self):
        return not (self.eaten_by or self.ghost)

    def possible_movements(self) -> list[Movement]:
        """Get the list of the piece's possible movements
        This method only checks for :
            - movement capabilities
            - pieces that stop the movement

        Returns:
            list[Movement]
        """
        return []

    def legal_movements(self, board: 'Board') -> list[Movement]:
        return [
            move
            for move in self.possible_movements()
            if move.in_board(board).is_legal_now()
        ]

    def moved(self, movement: Movement) -> None:
        """Should be executed after the piece has been moved by the given movement

        Args:
            movement (Movement): The movement the piece made
        """

    def unmoved(self, movement: Movement) -> None:
        """Should be executed after that the given movement has been canceled

        Args:
            movement (Movement): The movement the piece made
        """

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

    def unmoved(self, movement: Movement) -> None:
        if movement.in_board(self.board) is self.__moved_from:
            self.__moved_from = None

        return super().unmoved(movement)

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
            use_legals_movements_in: Board | Literal[False] = False,
            should_be: bool = True
    ):
        self.__pieces = filter(
            lambda p: (
                position in map(
                    lambda m: m.to_position,

                    p.legal_movements(use_legals_movements_in)
                    if use_legals_movements_in is not False
                    else p.possible_movements(),
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
