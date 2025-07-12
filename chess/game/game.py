from typing import TYPE_CHECKING
from chess.board import Board
from chess.pieces.bishop import Bishop
from chess.pieces.king import King
from chess.pieces.knight import Knight
from chess.pieces.pawn import Pawn
from chess.pieces.queen import Queen
from chess.pieces.rook import Rook
from chess.players._player import Player
from chess.position import Position
from chess.movement.board_movement import BoardMovements

if TYPE_CHECKING:
    from chess.movement.board_movement import BoardMovement
    from chess.movement.movement import Movement


class ChessGame:
    def __init__(self, players: tuple[Player, Player], board: Board | None = None) -> None:
        assert players[0].direction != players[1].direction, "Players has the same direction !"

        self.moves = BoardMovements()
        self.players = players
        self.board = board if board is not None else Board()
        self.debug = False

        self.__state = "empty"
        if board is None:
            self.init_board()

    def now_playing(self):
        return self.players[len(self.moves) % 2]

    def now_opponent(self):
        return self.players[(len(self.moves) + 1) % 2]

    def opponent_of(self, player: Player):
        return self.players[self.players[0].is_white == player.is_white]

    @property
    def state(self):
        return self.__state

    @property
    def is_playing(self):
        return self.state == "playing"

    def start(self):
        self.__state = "playing"
        return self

    def pause(self):
        self.__state = "paused"
        return self

    def resume(self):
        self.__state = "playing"
        return self

    def stop(self):
        self.__state = "stopped"
        return self

    def reset(self, remove_pieces=False):
        self.__state = "idle"
        if remove_pieces:
            self.board._pieces = []
        else:
            self.init_board()
        return self

    def __clear_console(self):
        # Clears the terminal screen
        print(chr(27) + "[2J")

    def autoplay(self, message: str | None = None) -> None:
        if self.state == "paused":
            input("Game paused. Press ENTER to resume.")
            self.resume()
            return self.autoplay("Game resumed.")

        if not self.is_playing:
            return

        if not self.debug:
            self.__clear_console()

        player = self.now_playing()
        print(f"Playing: {player}", end="")
        print(f" - {message}" if message else "")
        print(f"Moves: {self.moves}")
        print(self.board.with_coordonates().as_reversed(player.is_black))

        request = player.get_move(self)
        move_result = request if isinstance(
            request, str
        ) else self.exec_move(request)

        if isinstance(move_result, str):
            return self.autoplay(move_result)

        move, info = move_result

        check, check_mate = info["check"]
        if check_mate:
            self.__clear_console()
            print("Echec et mat : Partie terminée.")
            print(self.board.as_reversed(False).with_coordonates())
            self.stop()

        self.moves.register(move)
        return self.autoplay("Echec !" if check else None)

    def exec_move(self, move: 'Movement|BoardMovement'):
        if self.__state != "playing":
            return "Impossible d'executer le movement. La partie n'est pas active."

        gm = move.in_board(self.board)
        try:
            return (gm, gm.with_check_mate().validate())
        except AssertionError as err:
            gm.unvalidate()
            return str(err.args[0])

    @property
    def black_player(self):
        return self.players[self.players[1].is_black]

    @property
    def white_player(self):
        return self.players[self.players[1].is_white]

    def init_board(self):
        assert self.white_player.is_black != self.black_player.is_black, "Players has the same direction ! Game cannot init the board."

        self.board._pieces = []
        # Pawns
        for x_axis in Position.valid_board_x:
            for (white, pawn_y) in enumerate([7, 2]):
                Pawn(
                    self.board,
                    self.white_player if white else self.black_player,
                    f"{x_axis}{pawn_y}"
                )

        # Rooks
        Rook(self.board, self.white_player, "a1")
        Rook(self.board, self.white_player, "h1")
        Rook(self.board, self.black_player, "a8")
        Rook(self.board, self.black_player, "h8")

        # Knight
        Knight(self.board, self.white_player, "b1")
        Knight(self.board, self.white_player, "g1")
        Knight(self.board, self.black_player, "b8")
        Knight(self.board, self.black_player, "g8")

        # Bishop
        Bishop(self.board, self.white_player, "c1")
        Bishop(self.board, self.white_player, "f1")
        Bishop(self.board, self.black_player, "c8")
        Bishop(self.board, self.black_player, "f8")

        queen_x = "e" if self.white_player.is_black else "d"
        king_x = "e" if queen_x == "d" else "d"

        Queen(self.board, self.white_player, f"{queen_x}1")
        Queen(self.board, self.black_player, f"{queen_x}8")

        King(self.board, self.white_player, f"{king_x}1")
        King(self.board, self.black_player, f"{king_x}8")

        self.__state = "ready"
