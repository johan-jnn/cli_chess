from typing import TYPE_CHECKING, Literal
from chess.boards.board import Board
from chess.boards.normal import NormalBoard
from chess.players._player import DrawReason, Player

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

        self.players = players
        self.black_player = players[players[1].is_black]
        self.white_player = players[players[1].is_white]

        self.board = board if board is not None else NormalBoard()
        self.debug = False

        self.__state = "empty"
        self.__winner: None | Player = None
        self.__draw: DrawReason | Literal[False] = False

        if board is None:
            self.setup_board()

        self.reset()

    def now_playing(self):
        return self.players[len(self.board.moves) % 2]

    def now_opponent(self):
        return self.players[(len(self.board.moves) + 1) % 2]

    def opponent_of(self, player: Player):
        return self.players[self.players[0].is_white == player.is_white]

    @property
    def has_winner_or_draw(self):
        return self.__winner or self.__draw

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
        self.__winner = None
        self.board.empty()
        self.__state = "empty"

        if not remove_pieces:
            self.setup_board()
            self.__state = "idle"

        return self

    def _clear_console(self):
        # Clears the terminal screen
        print(chr(27) + "[2J")

    def autoplay(self, message: str = ""):
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
        print(f"Moves: {self.board.moves}")
        print(self.board.with_coordonates().as_reversed(player.is_black))

        request = player.get_move(self)
        if isinstance(request, str):
            return self.autoplay(request)

        try:
            movement = self.play(request)
        except AssertionError as err:
            return self.autoplay(str(err.args[0]))

        if self.has_winner_or_draw:
            self._clear_console()

            if isinstance(self.has_winner_or_draw, Player):
                print(
                    f"Echec et mat : Partie terminée. {self.has_winner_or_draw} remporte la partie."
                )
            else:
                print(f"Nule ! Raison: {self.has_winner_or_draw}")
            print(self.board.as_reversed(False).with_coordonates())
            return

        opponent_consequences = movement.consequences('opponent')
        assert opponent_consequences is not None

        return self.autoplay("Echec !" if opponent_consequences.with_check().is_checked else "")

    def play(self, move: 'Movement|str') -> 'BoardMovement':
        """Play and register the move, then check for check, checkmate and draw.

        Args:
            move (Movement|str): The movement to execute

        Raises:
            err: If the game is not playing or there is a move error

        Returns:
            BoardMovement: The movement that have been playing with all the informations filled
        """
        assert self.is_playing, "Impossible d'executer le movement. La partie n'est pas active."

        from chess.movement.board_movement import BoardMovement

        request = BoardMovement.decode(
            move, self.board, self.now_playing()
        ) if isinstance(move, str) else move
        assert request is not False, "Invalid movement."

        movement = request.in_board(self.board)

        try:
            movement.validate(True)
        except AssertionError as err:
            movement.unvalidate()
            raise err

        opponent_status = movement.consequences('opponent')
        assert opponent_status is not None, "Cannot validate status of the opponent."
        opponent_status.with_checkmate().with_draw()

        if opponent_status.is_check_mate:
            self.__winner = self.now_playing()
            self.board.get_king_of(
                self.now_opponent()
            ).toggle_checkmate_representation(True)
            self.stop()
        elif opponent_status.is_draw:
            self.__draw = opponent_status.is_draw
            self.stop()

        return movement

    def setup_board(self):
        assert self.white_player.is_black != self.black_player.is_black, "Players has the same direction ! Game cannot init the board."

        self.board.setup(self.white_player, self.black_player)

        self.__state = "ready"
