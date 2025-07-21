from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    from chess.boards.board import Board


class Position:
    def __init__(self, x: str, y: int | None = None) -> None:
        self.__x, self.__y = self.__get_xy(x, y)
        self._validated_in_board: 'Board|None' = None

    @property
    def in_board(self):
        return self._validated_in_board

    @property
    def board(self):
        assert self._validated_in_board is not None, "Position has not been validated in board"
        return self._validated_in_board

    @staticmethod
    def __get_xy(x: str, y: int | None = None):
        if y is None:
            assert len(x) == 2, "Invalid xy position value"
            [x, _y] = x
            y = int(_y)

        return x, y

    @staticmethod
    def validate(in_board: 'Board', x: str, y: int | None = None):
        x, y = Position.__get_xy(x, y)
        assert x in in_board.X_RANGE, "Invalid x position or value"
        assert y in in_board.Y_RANGE, "Invalid y position or value"

        position = Position(x, y)
        position._validated_in_board = in_board
        return position

    @property
    def x(self):
        return self.__x

    @property
    def y(self):
        return str(self.__y)

    @property
    def x_index(self):
        return self.board.X_RANGE.index(self.__x)

    @property
    def y_index(self):
        return self.board.Y_RANGE.index(self.__y)

    @property
    def raw_x(self):
        return self.__x

    @property
    def raw_y(self):
        return self.__y

    @property
    def raw_xy(self) -> tuple[str, int]:
        return self.raw_x, self.raw_y

    def move(self):
        """Get the movement builder from this position
        """
        from chess.movement.movement import MovementBuilder
        return MovementBuilder(self)

    def copy_from(self, position: 'Position') -> Self:
        self.__x, self.__y = position.raw_xy
        return self

    def clone(self):
        pos = Position(*self.raw_xy)
        pos._validated_in_board = self._validated_in_board
        return pos

    def __eq__(self, value: object) -> bool:
        if isinstance(value, Position):
            return value.raw_xy == self.raw_xy

        return False

    def __str__(self) -> str:
        return self.x + self.y
