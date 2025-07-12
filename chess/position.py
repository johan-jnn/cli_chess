from typing import Self


class Position:
    valid_board_x = list("abcdefgh")
    valid_board_y = list(range(1, 9))

    def __init__(self, x: str, y: int | None = None) -> None:
        self.__x, self.__y = Position.validate_xy(x, y)

    @staticmethod
    def validate_xy(x: str, y: int | None = None) -> tuple[str, int]:
        if y is None:
            assert len(x) == 2, "Invalid xy position value"
            [x, _y] = x
            y = int(_y)

        assert x in Position.valid_board_x, "Invalid x position or value"
        assert y in Position.valid_board_y, "Invalid y position or value"

        return x, y

    @property
    def x(self):
        return self.__x

    @property
    def y(self):
        return str(self.__y)

    @property
    def x_index(self):
        return Position.valid_board_x.index(self.__x)

    @property
    def y_index(self):
        return Position.valid_board_y.index(self.__y)

    @property
    def raw_x(self):
        return self.__x

    @property
    def raw_y(self):
        return self.__y

    @property
    def raw_xy(self) -> tuple[str, int]:
        return self.raw_x, self.raw_y

    def to(self, position: 'Position'):
        """Get the movement from this position to another
        """
        from chess.movement.movement import Movement
        return Movement(self, position)

    def move(self):
        """Get the movement builder from this position
        """
        from chess.movement.movement import MovementBuilder
        return MovementBuilder(self)

    def copy_from(self, position: 'Position') -> Self:
        self.__x, self.__y = position.raw_xy
        return self

    def clone(self):
        return Position(*self.raw_xy)

    def __eq__(self, value: object) -> bool:
        if isinstance(value, Position):
            return value.raw_xy == self.raw_xy

        return False

    def __str__(self) -> str:
        return self.x + self.y
