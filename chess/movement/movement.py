from typing import TYPE_CHECKING
from chess.position import Position

if TYPE_CHECKING:
    from chess.pieces.king import CastlingDirection
    from chess.pieces._piece import Piece
    from chess.pieces.pawn import Pawn
    from chess.boards.board import Board


class Movement:
    # https://regex101.com/r/F0ncE1/4
    MOVE_REGEX = r"^(?:(?:(?P<piece>[prnbkq])?\s*(?P<from_col>[a-h])?(?P<from_row>[1-8])?\s*(?P<capture>x)?\s*(?P<to>[a-h][1-8]))\s*(?:[=/]?\s*(?P<promotion>[rnqb]))?|(?P<k_castling>(?P<char>[0O])\s*-\s*(?P=char))|(?P<q_castling>(?P<char2>[0O])\s*-\s*(?P=char2)\s*-\s*(?P=char2)))(?:\s*(?P<check>\+)|(?P<check_mate>#))?\s*(?P<draw_offer>\(=\))?$"

    def __init__(self, from_position: Position, to_position: Position) -> None:
        self.from_position = from_position.clone()
        self.to_position = to_position.clone()
        self._computed_notation: str | None = None

        self.__cascade_with: Movement | None = None
        self.with_piece_eaten: 'Piece|None' = None
        self.with_promotion: 'tuple[Pawn, Piece] | None' = None
        self.with_castling: 'CastlingDirection|None' = None

    def cascading(self, with_movement: 'Movement'):
        self.__cascade_with = with_movement
        return self

    def not_cascading(self):
        self.__cascade_with = None
        return self

    @property
    def cascade(self):
        """The return movement is executed after the parent movement is made.
        """
        return self.__cascade_with

    def in_board(self, board: 'Board'):
        from chess.movement.board_movement import BoardMovement
        return BoardMovement(self, board)

    @property
    def notation(self):
        return (
            self._computed_notation
            or self.__identifier__()
        )

    @property
    def difference(self):
        return (
            self.to_position.x_index - self.from_position.x_index,
            self.to_position.y_index - self.from_position.y_index
        )

    @property
    def distance(self):
        diff = self.difference
        return (abs(diff[0]), abs(diff[1]))

    def __identifier__(self):
        return f"{self.from_position} -> {self.to_position}"

    def __eq__(self, value: object) -> bool:
        if isinstance(value, Movement):
            return self.__identifier__() == value.__identifier__()

        return value == self

    def __str__(self) -> str:
        return self.notation + (
            f" ==> {self.cascade}"
            if self.cascade else ""
        )


class MovementBuilder:
    def __init__(self, init_position: Position) -> None:
        self.__init = init_position
        self.__xy = -1, -1
        self.reset()

    def reset(self):
        self.__xy = self.__init.x_index, self.__init.y_index
        return self

    def position(self):
        assert 0 <= self.__xy[0] < len(
            Position.valid_board_x), "Movement overflow on x"
        assert 0 <= self.__xy[1] < len(
            Position.valid_board_y), "Movement overflow on y"

        return Position(
            Position.valid_board_x[self.__xy[0]],
            Position.valid_board_y[self.__xy[1]]
        )

    def safe_position(self):
        try:
            return self.position()
        except AssertionError:
            return None

    def movement(self):
        return Movement(self.__init, self.position())

    def safe_movement(self):
        try:
            return self.movement()
        except AssertionError:
            return None

    def setX(self, x: str):
        self.__xy = Position.valid_board_x.index(x), self.__xy[1]
        return self

    def setY(self, y: int):
        self.__xy = self.__xy[0], Position.valid_board_y.index(y)
        return self

    def addX(self, add: int, direction: int = 1):
        self.__xy = self.__xy[0] + add * direction, self.__xy[1]
        return self

    def addY(self, add: int, direction: int = 1):
        self.__xy = self.__xy[0], self.__xy[1] + add * direction
        return self

    def addXY(self, x: int, y: int, directions: int | tuple[int, int] = 1):
        dx, dy = directions if isinstance(
            directions, tuple) else (directions, directions)
        self.addX(x, dx)
        self.addY(y, dy)
        return self

    def to(self, position: Position | str):
        if isinstance(position, str):
            position = Position(position)
        self.__xy = position.x_index, position.y_index

        return self
