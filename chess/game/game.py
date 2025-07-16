from typing import TYPE_CHECKING
from chess.boards.board import Board
from chess.boards.normal import NormalBoard
from chess.players._player import Player
from chess.movement.board_movement import BoardMovements

if TYPE_CHECKING:
    from chess.movement.board_movement import BoardMovement
    from chess.movement.movement import Movement


class ChessGame:
    def __init__(self, players: tuple[Player, Player], board: Board | None = None) -> None:
        """Create a new chess game

        Args:
            players (tuple[Player, Player]): The players of this game, ordered by the playing position (first is first to play)
            board (Board | None, optional): The board the players will play in. Defaults to None (generates a new normal board with basic pieces position).
        """
        assert players[0].direction != players[1].direction, "Players has the same direction !"

        self.moves = BoardMovements()
        self.players = players
        self.board = board if board is not None else NormalBoard()
        self.debug = False

        self.__state = "empty"
        self.__winner: None | Player = None

        if board is None:
            self.setup_board()

        self.reset()

    def now_playing(self):
        return self.players[len(self.moves) % 2]

    def now_opponent(self):
        return self.players[(len(self.moves) + 1) % 2]

    def opponent_of(self, player: Player):
        return self.players[self.players[0].is_white == player.is_white]

    @property
    def winner(self):
        return self.__winner

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
        self.__winner = None
        self.board.get_king_of(
            self.now_playing()).toggle_checkmate_representation(False)
        self.board.get_king_of(
            self.now_opponent()).toggle_checkmate_representation(False)

        if remove_pieces:
            self.board._pieces = []
            self.__state = "empty"

        return self

    def _clear_console(self):
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
            self._clear_console()

        player = self.now_playing()
        print(f"Playing: {player}", end="")
        print(f" - {message}" if message else "")
        print(f"Moves: {self.moves}")
        print(self.board.with_coordonates().as_reversed(player.is_black))

        request = player.get_move(self)
        if isinstance(request, str):
            return self.autoplay(request)

        try:
            _, info = self.play(request)
        except AssertionError as err:
            return self.autoplay(str(err.args[0]))

        check, check_mate = info['check']
        if check_mate:
            self._clear_console()
            print("Echec et mat : Partie terminée.")
            print(self.board.as_reversed(False).with_coordonates())
            self.stop()

        return self.autoplay("Echec !" if check else None)

    def __exec_move(self, move: 'Movement|BoardMovement'):
        if self.__state != "playing":
            return "Impossible d'executer le movement. La partie n'est pas active."

        gm = move.in_board(self.board)
        try:
            return (gm, gm.with_check_mate().validate())
        except AssertionError as err:
            gm.unvalidate()
            return str(err.args[0])

    def play(self, move: 'Movement|BoardMovement|str'):
        from chess.movement.board_movement import BoardMovement

        request = BoardMovement.decode(
            move, self.board, self.now_playing()
        ) if isinstance(move, str) else move
        assert request is not False, "Invalid movement."

        move_result = self.__exec_move(request)

        assert not isinstance(move_result, str), move_result
        move, info = move_result

        if info['check'][1]:
            self.__winner = self.now_playing()
            self.board.get_king_of(
                self.now_opponent()
            ).toggle_checkmate_representation(True)

            self.stop()

        self.moves.register(move)
        return move, info

    @property
    def black_player(self):
        return self.players[self.players[1].is_black]

    @property
    def white_player(self):
        return self.players[self.players[1].is_white]

    def setup_board(self):
        assert self.white_player.is_black != self.black_player.is_black, "Players has the same direction ! Game cannot init the board."

        self.board.setup(self.white_player, self.black_player)

        self.__state = "ready"
