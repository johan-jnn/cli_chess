
from typing import TYPE_CHECKING, Literal
from chess.movement.movement import Movement

if TYPE_CHECKING:
    from chess.game.game import ChessGame


class Player:
    def __init__(self, direction: Literal[-1, 1], name: str | None = None) -> None:
        """Creates a new player

        Args:
            direction (int): The direction of the player. Whites are defined by a direction > 0 and blacks by a direction < 0
            name (str, optional): The name of the player. Defaults to the color of the player.
        """
        assert direction, "Player's direction cannot be 0"

        self.direction = direction
        self.name = name or ("Whites" if self.is_white else "Blacks")

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
