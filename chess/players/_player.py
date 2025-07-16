
from typing import TYPE_CHECKING, Literal
from chess.movement.movement import Movement

if TYPE_CHECKING:
    from chess.game.game import ChessGame
    from chess.boards.board import Board


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

    def verify_status(self, in_board: 'Board', pre_compute_checked=True, pre_compute_endgame=False):
        return StatusVerifier(self, in_board, pre_compute_checked, pre_compute_endgame)

    @property
    def is_black(self):
        return self.direction < 0

    @property
    def is_white(self):
        return self.direction > 0

    def __str__(self) -> str:
        return self.name


class StatusVerifier():
    def __init__(self, player: Player, board: 'Board', direct_verify_for_checked=False, direct_verify_for_end_game=False) -> None:
        self.__player = player
        self.__board = board
        self.__king = board.get_king_of(player)

        self.is_checked = None

        self.is_check_mate = None
        self.is_draw = None

        if direct_verify_for_checked:
            self.verify_for_check()
        if direct_verify_for_end_game:
            self.verify_for_end_game()

    def verify_for_check(self, verify=True):
        """
        Set the value of self.is_checked (if the player's king position is contested by opponent's pieces)
        """
        if verify:
            self.is_checked = self.board.pieces.of(
                self.player, False
            ).contesting(self.__king.position).exist()
        else:
            self.is_checked = None

        return self

    def verify_for_end_game(self, verify=True):
        if verify:
            if self.is_checked is None:
                self.verify_for_check(True)
            player_checked = self.is_checked or False
            player_can_move = self.__is_able_to_move()

            self.is_check_mate = player_checked and not player_can_move
            self.is_draw = not (player_checked or player_can_move)
        else:
            self.is_draw = self.is_check_mate = None

        return self

    @property
    def player(self):
        return self.__player

    @property
    def board(self):
        return self.__board

    def __is_able_to_move(self):
        for piece in self.board.pieces.of(self.player):
            if piece.legal_movements(self.board):
                return True
        return False
