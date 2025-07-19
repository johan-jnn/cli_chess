from typing import Callable, Iterator
from chess.movement.board_movement import BoardMovement
from chess.players._player import Player
from chess.position import Position


class Board:
    EMPTY_EVEN_CASE_CHAR = "▣"
    EMPTY_ODD_CASE_CHAR = "□"

    JOIN_BOARD_LINES_BY = "\n"
    JOIN_BOARD_CASES_BY = " "
    BOARD_COORDONATES_SEPARATORS = ["|", ""]

    def __init__(self) -> None:
        from chess.pieces._piece import Piece

        # Autofilled by Piece class
        self._pieces: list[Piece] = []

        self.__show_board_coordonates = False
        self.__reverse_board_y = False
        self.moves = BoardMovements()

    @property
    def pieces(self):
        """Get all the playable pieces of the board
        """
        return self.all_pieces.playable()

    @property
    def all_pieces(self):
        """Get all the pieces (even the not playable ones) of the board
        """
        from chess.pieces._piece import PieceList
        return PieceList(self._pieces)

    def empty(self):
        self._pieces = []

    def setup(self, whites: Player, blacks: Player):
        pass

    def get_king_of(self, player: Player, get_opponent_king=False):
        from chess.pieces.king import King
        for piece in self.pieces.of(player, not get_opponent_king):
            if isinstance(piece, King):
                return piece
        raise LookupError("The player has no king.")

    def with_coordonates(self, show=True):
        self.__show_board_coordonates = show
        return self

    def as_reversed(self, reverse=True):
        self.__reverse_board_y = reverse
        return self

    def __eq__(self, value):
        return hash(self) == value

    def state_identifier(self):
        representations = [
            f"{int(piece.player.is_white)}{piece.NOTATION}{piece.position}"
            for piece in self.pieces.get()
        ]

        representations.sort()
        return "".join(representations)

    def __hash__(self) -> int:
        return hash(self.state_identifier())

    def __str__(self) -> str:
        board = []

        for (y_index, y_axis) in enumerate(Position.valid_board_y):
            line = []
            for (x_index, x_axis) in enumerate(Position.valid_board_x):
                piece = self.pieces.at(x_axis, y_axis).first()
                if piece:
                    line.append(str(piece))
                else:
                    line.append(
                        self.EMPTY_EVEN_CASE_CHAR if x_index % 2 == (
                            y_index % 2) else self.EMPTY_ODD_CASE_CHAR
                    )
            if self.__show_board_coordonates:
                line.append(self.BOARD_COORDONATES_SEPARATORS[0] + str(y_axis))
            board.append(self.JOIN_BOARD_CASES_BY.join(line))

        # The reverse feature is for human
        # As the chess is read from bottom to top,
        # and stored from top to bottom, we
        # reverse the board only if we read from
        # top to bottom (opposite of human chess reading)
        if not self.__reverse_board_y:
            board.reverse()

        if self.__show_board_coordonates:
            if self.BOARD_COORDONATES_SEPARATORS[1]:
                board.append(self.JOIN_BOARD_CASES_BY.join(
                    self.BOARD_COORDONATES_SEPARATORS[1] * len(Position.valid_board_x)))
            board.append(self.JOIN_BOARD_CASES_BY.join(Position.valid_board_x))
        return self.JOIN_BOARD_LINES_BY.join(board)


class BoardMovements:
    @staticmethod
    def first_of(movement: BoardMovement):
        while movement.depends_on:
            movement = movement.depends_on
        return movement

    @staticmethod
    def n_of(movement: BoardMovement, n: int):
        _n = n
        while n > 0:
            if movement.depends_on is None:
                raise IndexError(f"There is no {_n} movements available.")
            movement = movement.depends_on
            n -= 1
        return movement

    @staticmethod
    def iter_of(movement: BoardMovement) -> Iterator[BoardMovement]:
        values = []
        _m: BoardMovement | None = movement
        while _m:
            values.append(_m)
            _m = _m.depends_on

        return iter(values)

    @staticmethod
    def len_of(movement: BoardMovement, count_only_children: bool = False):
        i = int(not count_only_children)
        while movement.depends_on:
            movement = movement.depends_on
            i += 1
        return i

    @staticmethod
    def first_when_of(movement: BoardMovement, validate: int | Callable[[BoardMovement], bool]):
        i = 0
        _m: BoardMovement | None = movement
        while _m:
            if isinstance(validate, int) and i == validate:
                return _m
            if isinstance(validate, Callable) and validate(_m):
                return _m
            _m = _m.depends_on
            i += 1

        return None

    def __init__(self) -> None:
        self.__first_movement: BoardMovement | None = None
        self.__last_movement: BoardMovement | None = None

    @property
    def first(self):
        return self.__first_movement

    @property
    def last(self):
        return self.__last_movement

    def register(self, movement: BoardMovement):
        if self.__last_movement is not None:
            movement.depends_on = self.__last_movement
        self.__last_movement = movement

        if self.__first_movement is None:
            self.__first_movement = movement

    def shift(self, n: int = 0):
        if self.last is None:
            return
        movement = BoardMovements.n_of(self.last, n)
        self.__last_movement = movement.depends_on

        if self.__last_movement is None:
            self.__first_movement = None

        return movement

    def n(self, n: int):
        if self.last is None:
            return
        return BoardMovements.n_of(self.last, n)

    def __len__(self):
        if self.last is None:
            return 0
        return BoardMovements.len_of(self.last)

    def first_that(self, validate: int | Callable[[BoardMovement], bool]):
        if self.last is None:
            return
        return BoardMovements.first_when_of(self.last, validate)

    def manage_last(self):
        return LastMovementManager(self) if self.last else None

    def __iter__(self) -> Iterator[BoardMovement]:
        if self.last is None:
            return iter([])
        return BoardMovements.iter_of(self.last)

    def __str__(self) -> str:
        return " - ".join([str(m) for m in iter(self)])


class LastMovementManager(BoardMovement):
    def __init__(self, manager: BoardMovements) -> None:
        assert manager.last, "No movement in manager : cannot instanciate an empty LastMovementManager"
        self.__manager = manager
        self.__movement = manager.last
        self.__dict__.update(self.__movement.__dict__)

    def unvalidate(self):
        return self.undo()

    def undo(self):
        self.__movement.unvalidate()
        self.__manager.shift()
