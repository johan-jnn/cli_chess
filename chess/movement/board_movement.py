import re
from typing import TYPE_CHECKING, Callable, Iterator, Literal
from chess.movement.movement import Movement
from chess.pieces._piece import Piece
from chess.pieces.king import King
from chess.pieces.pawn import Pawn
from chess.position import Position

if TYPE_CHECKING:
    from chess.players._player import Player
    from chess.board import Board


class BoardMovement(Movement):

    @staticmethod
    def decode(move: str, board: 'Board', player: 'Player'):
        """Get the movement from the algebric movement notation

        Args:
            move (str): The algebric movement
            game (Board): The current game
            player (Player): The associed player to this movement.

        Raises:
            ValueError: If the player is not in the game
        """
        move_info = re.search(Movement.MOVE_REGEX, move, re.IGNORECASE)
        if move_info is None:
            return False

        if move_info.group('k_castling'):
            return board.get_king_of(player).position.move().addX(2).get()
        if move_info.group('q_castling'):
            return board.get_king_of(player).position.move().addX(-2).get()

        to, piece, from_col, from_row = move_info.group(
            'to', 'piece', 'from_col', 'from_row'
        )

        to_position = Position(to)
        found: Movement | Literal[False] = False

        for player_piece in board.pieces.of(player):
            movement = Movement(player_piece.position, to_position)

            if piece and piece.lower() != player_piece.NOTATION.lower():
                continue

            # Uncomment the following to force indicating the piece if it is not a pawn
            # if not (piece or isinstance(player_piece, Pawn)):
            #     continue

            if from_col and player_piece.position.x != from_col:
                continue

            if from_row and player_piece.position.y != from_row:
                continue

            if movement not in player_piece.legal_movements(board):
                continue

            if found:
                return False
            found = movement

        return found

    def __init__(
            self,
            positions: tuple[Position, Position] | Movement,
            board: 'Board',
            depends_on: 'BoardMovement|None' = None,
    ) -> None:
        if isinstance(positions, Movement):
            super().__init__(positions.from_position, positions.to_position)
        else:
            super().__init__(positions[0], positions[1])
        self.board = board
        self.depends_on = depends_on

        self.__verify_check_mate = False

        self.__board_hash_after: int | None = None
        self.__eaten_piece: Piece | None = None
        self.__promotion: tuple[Pawn, Piece] | None = None
        self.__made_check: tuple[bool, None | bool] = (False, None)

    def in_game(self, board: 'Board'):
        return self

    def with_check_mate(self, verify=True):
        self.__verify_check_mate = verify
        return self

    def is_legal_now(self):
        piece = self.board.pieces.at(self.from_position).first()
        if piece is None:
            return False

        reset_check_mate_verify_to = self.__verify_check_mate
        self.with_check_mate(False)

        is_pawn = isinstance(piece, Pawn)
        reset_promotion_to = is_pawn and piece.promotion_forced_to
        if is_pawn:
            piece.will_promote_as(piece.PROMOTABLE_AS[0][1])

        legal = False
        try:
            self.validate(False)
            legal = not self.board.get_king_of(piece.player).is_check()
            self.unvalidate()
        except AssertionError:
            pass

        if is_pawn and reset_promotion_to:
            piece.will_promote_as(reset_promotion_to)

        self.with_check_mate(reset_check_mate_verify_to)
        return legal

    def validate(self, compute_notation=True):
        assert self.__board_hash_after is None, "The movement has already been validated."
        piece = self.board.pieces.at(self.from_position).first()
        assert piece is not None, "Cannot validate the movement: no piece at the start position"

        eaten = self.board.pieces.at(self.to_position).first()
        if eaten is not None:
            assert eaten.player != piece.player, "Cannot eat your own piece"
            assert isinstance(eaten, King), "Cannot eat a king."
            eaten.eaten_by = piece
            self.__eaten_piece = eaten

        piece.position.copy_from(self.to_position)
        piece.moved(self)

        promotion = self.board.pieces.at(
            self.to_position
        ).exept(piece).first()
        if isinstance(piece, Pawn) and promotion:
            self.__promotion = (piece, promotion)

        opponent_king = self.board.get_king_of(piece.player, True)
        self.__made_check = (
            opponent_king.is_check(),
            opponent_king.is_check_mate(
                self.board
            ) if self.__verify_check_mate else None
        )

        self.__board_hash_after = hash(self.board)

        if compute_notation:
            self.__compute_notation()

        assert self.info is not None, "Program error: info cannot be None !"
        return self.info

    @property
    def info(self):
        """Get the information of the validated movement

        ## Types
            ### Info: 
            dict{
                check: (check: bool, check_mate: bool|None), 
                    #? For check_mate, a None value means that the mate has not been checked.
                    #? Call the method with_check_mate() before validating the movement to include the check_mate verification
                promotion: None | dict{
                    from: Pawn,
                    to: Piece
                },
                eaten: None | Piece,
                board_hash_result: int
            }

        Returns:
            None|Info: If the movement has not been validated, None is returned.
        """
        if self.__board_hash_after is None:
            return self.__board_hash_after
        return {
            "check": self.__made_check,
            "promotion": {
                "from": self.__promotion[0],
                "to": self.__promotion[1]
            } if self.__promotion else None,
            "eaten": self.__eaten_piece,
            "board_hash_result": self.__board_hash_after
        }

    def unvalidate(self):
        assert hash(
            self.board
        ) == self.__board_hash_after, "The movement can't be unvalidated because the board is not at the right position."

        piece = self.__promotion[0] if self.__promotion else self.board.pieces.at(
            self.to_position
        ).first()
        assert piece is not None, "Cannot unvalidate the movement: no piece at the end position"

        piece.position.copy_from(self.from_position)
        piece.unmoved(self)

        if self.__eaten_piece is not None:
            self.__eaten_piece.eaten_by = None
            self.__eaten_piece = None

        self.__board_hash_after = None
        self._computed_notation = None

    def __compute_notation(self):
        """
              Compute the generated movement in the __computed_notation property.
              This method must be called **AFTER** the movement has been fully made.
              Warning: call this method only once : the computed notation will be relative to the board current pieces positions
        """
        assert hash(
            self.board
        ) == self.__board_hash_after, "The notation cannot be computed as the board is not valid."

        piece = self.__promotion[0] if self.__promotion else (
            self.board.pieces.at(self.to_position).playable().first()
        )
        assert piece is not None, "The movement cannot be linked to the given board : no piece at the end position"

        piece.ghost = True

        # (x, y)
        use_helpers = [False, False]

        for other_piece in self.board.pieces.of(piece.player).type(type(piece)).exept(piece):
            if self.to_position in [m.to_position for m in other_piece.legal_movements(self.board)]:
                use_helpers[0] = (
                    piece.position.y == other_piece.position.y
                ) or use_helpers[0]

                use_helpers[1] = (
                    piece.position.x == other_piece.position.x
                ) or use_helpers[1]

            if use_helpers[0] and use_helpers[1]:
                break

        piece.ghost = False

        self._computed_notation = (
            "" if isinstance(piece, Pawn) else str(piece)
        ) + (
            self.from_position.x if use_helpers[0] else ""
        ) + (
            self.from_position.y if use_helpers[1] else ""
        ) + (
            "x" if self.__eaten_piece else ""
        ) + (
            str(self.to_position)
        ) + (
            self.__promotion[1].NOTATION.upper() if self.__promotion else ""
        ) + (
            "#" if self.__made_check[1] else
            "+" if self.__made_check[0] else ""
        )


class BoardMovements:
    @staticmethod
    def first_of(movement: BoardMovement):
        while movement.depends_on:
            movement = movement.depends_on
        return movement

    @staticmethod
    def n_of(movement: BoardMovement, n: int):
        _n = n
        while n > 0:
            if movement.depends_on is None:
                raise IndexError(f"There is no {_n} movements available.")
            movement = movement.depends_on
            n -= 1
        return movement

    @staticmethod
    def iter_of(movement: BoardMovement) -> Iterator[BoardMovement]:
        values = []
        _m: BoardMovement | None = movement
        while _m:
            values.append(_m)
            _m = _m.depends_on

        return iter(values)

    @staticmethod
    def len_of(movement: BoardMovement, count_only_children: bool = False):
        i = int(not count_only_children)
        while movement.depends_on:
            movement = movement.depends_on
            i += 1
        return i

    @staticmethod
    def first_when_of(movement: BoardMovement, validate: int | Callable[[BoardMovement], bool]):
        i = 0
        _m: BoardMovement | None = movement
        while _m:
            if isinstance(validate, int) and i == validate:
                return _m
            if isinstance(validate, Callable) and validate(_m):
                return _m
            _m = _m.depends_on
            i += 1

        return None

    def __init__(self) -> None:
        self.__first_movement: BoardMovement | None = None
        self.__last_movement: BoardMovement | None = None

    @property
    def first(self):
        return self.__first_movement

    @property
    def last(self):
        return self.__last_movement

    def register(self, movement: BoardMovement):
        if self.__last_movement is not None:
            movement.depends_on = self.__last_movement
        self.__last_movement = movement

        if self.__first_movement is None:
            self.__first_movement = movement

    def shift(self, n: int = 0):
        if self.last is None:
            return
        movement = BoardMovements.n_of(self.last, n)
        self.__last_movement = movement.depends_on

        if self.__last_movement is None:
            self.__first_movement = None

        return movement

    def n(self, n: int):
        if self.last is None:
            return
        return BoardMovements.n_of(self.last, n)

    def __len__(self):
        if self.last is None:
            return 0
        return BoardMovements.len_of(self.last)

    def first_that(self, validate: int | Callable[[BoardMovement], bool]):
        if self.last is None:
            return
        return BoardMovements.first_when_of(self.last, validate)

    def undo_last(self):
        movement = self.shift()
        if movement:
            movement.unvalidate()
        return movement

    def __iter__(self) -> Iterator[BoardMovement]:
        if self.last is None:
            return iter([])
        return BoardMovements.iter_of(self.last)

    def __str__(self) -> str:
        return " - ".join([str(m) for m in iter(self)])
