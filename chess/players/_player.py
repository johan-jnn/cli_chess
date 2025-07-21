
from enum import Enum
from typing import TYPE_CHECKING, Literal
from chess.movement.movement import Movement

if TYPE_CHECKING:
    from chess.game.game import ChessGame
    from chess.boards.board import Board


class Player:
    WHITES_DIRECTION = 1
    BLACKS_DIRECTION = -1

    def __init__(self, direction: Literal[-1, 1], name: str | None = None) -> None:
        """Creates a new player

        Args:
            direction (int): The direction of the player. Whites are defined by a direction = 1 and blacks by a direction = -1
            name (str, optional): The name of the player. Defaults to the color of the player.
        """
        assert direction, "Player's direction cannot be 0"

        self.direction = direction
        self.name = name or ("Whites" if self.is_white else "Blacks")

    def get_move(self, game: 'ChessGame') -> Movement | str:
        """Get this player's next move
        """
        raise NotImplementedError("Missing move method on parent class.")

    def opponent_in(self, board: 'Board'):
        found = board.all_pieces.of(self, False).first()
        assert found is not None, "The player has no opponent in this board."
        return found.player

    def verify_status(self, in_board: 'Board', pre_compute_checked=True, pre_compute_checkmate=False, pre_compute_draw=False):
        return StatusVerifier(self, in_board, pre_compute_checked, pre_compute_checkmate, pre_compute_draw)

    @property
    def is_black(self):
        return self.direction == self.BLACKS_DIRECTION

    @property
    def is_white(self):
        return self.direction == self.WHITES_DIRECTION

    def __str__(self) -> str:
        return self.name


class DrawReason(Enum):
    STALEMATE = 0
    REPETITION = 1
    FIFTY_MOVE = 2
    SEVENTY_MOVE = 3
    MUTUAL_AGREEMENT = 4
    INSUFFICIENT_MATERIAL = 5
    NO_SEQUENCE = 6

    # In timed games
    TIME_ALLOTMENT_EXCEEDED = 7
    TIMEOUT_AS_UNCHECKMATEABLE = 8

    def __str__(self) -> str:
        return {
            DrawReason.STALEMATE: "Mouvement impossible",
            DrawReason.REPETITION: "Répétition du même mouvement 3 fois",
            DrawReason.FIFTY_MOVE: "50 mouvements sans aucune prise",
            DrawReason.MUTUAL_AGREEMENT: "Demande accepté",
            DrawReason.INSUFFICIENT_MATERIAL: "Materiel insuffisant"
        }.get(self, self.name)


class StatusVerifier():
    def __init__(self, player: Player, board: 'Board', with_check=False, with_checkmate=False, with_draw=False) -> None:
        self.__player = player
        self.__board = board
        self.__king = board.get_king_of(player)

        self.is_checked = None

        self.is_check_mate = None
        self.is_draw: None | DrawReason = None

        if with_check:
            self.with_check()
        if with_checkmate:
            self.with_checkmate()
        if with_draw:
            self.with_draw()

    def with_check(self, verify=True):
        self.is_checked = (
            self.board.pieces.of(
                self.player, False
            ).contesting(self.__king.position).exist()
        ) if verify and self.is_checked is None else self.is_checked

        return self

    def with_checkmate(self, verify=True):
        self.is_check_mate = (
            self.with_check().is_checked and not self.has_movable_piece()
        ) if verify and self.is_check_mate is None else self.is_check_mate

        return self

    def __find_draw_reason(self) -> DrawReason | None:
        from chess.pieces.bishop import Bishop
        from chess.pieces.king import King
        from chess.pieces.knight import Knight

        min_pieces, max_pieces = sorted([
            self.board.pieces.of(self.__player).type(King, False).get(),
            self.board.pieces.of(self.__player, False).type(
                King, False
            ).get()
        ], key=len)

        if (
            not min_pieces
            and len(max_pieces) == 1
            and isinstance(max_pieces[0], (Bishop, Knight))
        ) or (
            len(min_pieces) == len(max_pieces) == 1
            and isinstance(min_pieces[0], Bishop)
            and isinstance(max_pieces[0], Bishop)
        ):
            return DrawReason.INSUFFICIENT_MATERIAL

        if not (
            self.with_check().is_checked or self.has_movable_piece()
        ):
            return DrawReason.STALEMATE

        _cache_data_template = {
            "last_move": {
                "iterations": 0,
                "move": None
            },
            "no_capture_iterations": 0
        }
        cache = {
            "whites": _cache_data_template.copy(),
            "blacks": _cache_data_template.copy()
        }

        for movement in self.board.moves.iter("lifo"):
            piece = movement.validated_as
            assert piece is not None, "Error: movement has not been validated."
            cache_data = cache['whites'] if piece.player.is_white else cache['blacks']

            if movement.with_piece_eaten:
                cache_data['no_capture_iterations'] = 0
            else:
                cache_data['no_capture_iterations'] += 1
                if cache_data['no_capture_iterations'] >= 50:
                    return DrawReason.FIFTY_MOVE

            if cache_data['last_move']['move'] == movement:
                cache_data['last_move']['iterations'] += 1
                if cache_data['last_move']['iterations'] >= 3:
                    return DrawReason.REPETITION

            cache_data['last_move']['move'] = movement

    def with_draw(self, verify=True):
        if verify:
            self.is_draw = self.__find_draw_reason()

        return self

    @property
    def player(self):
        return self.__player

    @property
    def board(self):
        return self.__board

    def has_movable_piece(self):
        for piece in self.board.pieces.of(self.player):
            if piece.legal_movements():
                return True
        return False

    def unvalitate(self):
        """Deletes the cached values
        """
        self.is_checked = self.is_check_mate = self.is_draw = None
