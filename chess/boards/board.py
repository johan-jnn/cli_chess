from typing import Iterable, Literal
from chess.movement.board_movement import BoardMovement
from chess.players._player import Player
from chess.position import Position


class Board:
    EMPTY_EVEN_CASE_CHAR = "▣"
    EMPTY_ODD_CASE_CHAR = "□"

    JOIN_BOARD_LINES_BY = "\n"
    JOIN_BOARD_CASES_BY = " "
    BOARD_COORDONATES_SEPARATORS = ["|", ""]

    X_RANGE: list[str] = []
    Y_RANGE: list[int] = []

    def __init__(self) -> None:
        from chess.pieces._piece import Piece

        # Autofilled by Piece class
        self._pieces: list[Piece] = []

        self.__show_board_coordonates = False
        self.__reverse_board_y = False
        self.moves = MovementStack()

    def auto_setup_kings(self, whites: tuple[Player, str | Position], blacks: tuple[Player, str | Position]):
        from chess.pieces.king import King
        self._pieces = [
            piece
            for piece in self._pieces
            if not isinstance(piece, King)
        ]

        for (player, position) in (whites, blacks):
            King(self, player, str(position))

        return self

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

        for (y_index, y_axis) in enumerate(self.Y_RANGE):
            line = []
            for (x_index, x_axis) in enumerate(self.X_RANGE):
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
                    self.BOARD_COORDONATES_SEPARATORS[1] * len(self.X_RANGE)))
            board.append(self.JOIN_BOARD_CASES_BY.join(self.X_RANGE))
        return self.JOIN_BOARD_LINES_BY.join(board)


class MovementStack:
    def __init__(self, init_from: Iterable = []) -> None:
        self.__stack: list[BoardMovement] = list(init_from)

    def insert(self, movement: BoardMovement):
        return self.__stack.append(movement)

    def pop(self):
        return self.__stack.pop()

    def size(self):
        return len(self.__stack)

    def __len__(self):
        return self.size()

    def is_empty(self):
        return bool(self.size())

    def last(self):
        return LastMovementManager(self)

    def iter(self, direction: Literal['fifo', 'lifo'] = "fifo"):
        iter_to = self.__stack if direction == "fifo" else reversed(
            self.__stack
        )
        return iter(iter_to)

    def __str__(self) -> str:
        return " - ".join([
            str(m)
            for m in self.iter('lifo')
        ])


class LastMovementManager(BoardMovement):
    def __init__(self, manager: MovementStack) -> None:
        moves = list(manager.iter("lifo"))
        assert moves, "No movements in the stack."

        self.__manager = manager
        self.__movement = moves[0]
        self.__dict__.update(self.__movement.__dict__)

    def unvalidate(self):
        return self.cancel()

    def cancel(self):
        self.__movement.unvalidate()
        self.__manager.pop()
        return True
