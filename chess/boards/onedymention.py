from chess.boards.board import Board
from chess.pieces.knight import Knight
from chess.pieces.rook import Rook
from chess.players._player import Player
from chess.position import Position


class OneDymentionKnight(Knight):
    def contesting_positions(self) -> list[Position]:
        contesting = []

        for jump_dir in (-1, 1):
            position = self.position.move().addX(2, jump_dir).safe_position()
            if position is None:
                continue

            if (
                self.board.pieces.at(position).of(
                    self.player
                ).exist()
            ):
                continue

            contesting.append(position)
        return contesting


class OneDymentionBoard(Board):
    X_RANGE: list[str] = list("abcdefgh")
    Y_RANGE: list[int] = [1]

    def setup(self, whites: Player, blacks: Player):
        self.empty()

        self.auto_setup_kings(
            (whites, 'a1'),
            (blacks, 'h1')
        )

        OneDymentionKnight(self, whites, 'b1')
        Rook(self, whites, 'c1')

        Rook(self, blacks, 'f1')
        OneDymentionKnight(self, blacks, 'g1')
