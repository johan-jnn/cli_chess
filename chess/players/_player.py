
from typing import TYPE_CHECKING
from chess.movement.movement import Movement

if TYPE_CHECKING:
    from chess.game.game import ChessGame


class Player:
    def __init__(self, direction: int, name: str = "Player #?") -> None:
        assert direction, "Player's direction cannot be 0"

        self.direction = direction
        self.name = name

    def get_move(self, game: 'ChessGame') -> Movement | str:
        """Get this player's next move
        """
        raise NotImplementedError("Missing move method on parent class.")

    @property
    def is_black(self):
        return self.direction < 0

    @property
    def is_white(self):
        return self.direction > 0

    def __str__(self) -> str:
        return self.name
