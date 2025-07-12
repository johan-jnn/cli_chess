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
