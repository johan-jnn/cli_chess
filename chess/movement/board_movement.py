from re import search as reg_exec, IGNORECASE as REG_I
from typing import TYPE_CHECKING, Literal
from chess.movement.movement import Movement
from chess.players._player import StatusVerifier
from chess.position import Position

if TYPE_CHECKING:
    from chess.boards.board import Board
    from chess.players._player import Player


class BoardMovement(Movement):

    @staticmethod
    def decode(move: str, board: 'Board', player: 'Player') -> 'Literal[False]|Movement':
        """Get the movement from the algebric movement notation

        Args:
            move (str): The algebric movement
            game (Board): The current game
            player (Player): The associed player to this movement.

        Raises:
            ValueError: If the player is not in the game
        """
        from chess.pieces.king import CastlingDirection, King

        move_info = reg_exec(Movement.MOVE_REGEX, move, REG_I)
        if move_info is None:
            return False

        king = board.get_king_of(player)
        if move_info.group('k_castling'):
            return king.get_castle_movement(CastlingDirection.KING) or False

        if move_info.group('q_castling'):
            return king.get_castle_movement(CastlingDirection.QUEEN) or False

        to, piece, from_col, from_row = move_info.group(
            'to', 'piece', 'from_col', 'from_row'
        )

        from chess.pieces.pawn import Pawn
        to_position = Position(to)
        found: Movement | Literal[False] = False

        for player_piece in board.pieces.of(player):
            movement = Movement(player_piece.position, to_position)

            if piece and piece.lower() != player_piece.NOTATION.lower():
                continue

            if not (piece or isinstance(player_piece, Pawn)):
                continue

            if from_col and player_piece.position.x != from_col:
                continue

            if from_row and player_piece.position.y != from_row:
                continue

            if movement not in player_piece.legal_movements():
                continue

            if found:
                return False
            found = movement

        if found and piece and isinstance(piece, King):
            castling = piece.castle_type(found)
            if castling is not None:
                return BoardMovement.decode("0-0" + (
                    "-0" if castling == 'queen' else ""
                ), board, player)

        return found

    def __init__(
            self,
            positions: tuple[Position, Position] | Movement,
            board: 'Board',
            depends_on: 'BoardMovement|None' = None,
    ) -> None:
        if isinstance(positions, Movement):
            self.__dict__.update(positions.__dict__)
            if self.cascade:
                self.cascading(self.cascade.in_board(board))
        else:
            super().__init__(positions[0], positions[1])

        self.board = board
        self.depends_on = depends_on

        self.__board_hash_after: int | None = None

        self.__player_consequences: None | StatusVerifier = None
        self.__opponent_consequences: None | StatusVerifier = None

    def in_board(self, board: 'Board'):
        if board is self.board:
            return self
        return super().in_board(board)

    def consequences(self, of: Literal['player', 'opponent']):
        return self.__player_consequences if of == "player" else self.__opponent_consequences

    def validate(self, and_save=False):
        assert self.__board_hash_after is None, "The movement has already been validated."
        piece = self.board.pieces.at(self.from_position).first()
        assert piece is not None, "Cannot validate the movement: no piece at the start position"

        piece.move(self)

        self.__board_hash_after = hash(self.board)

        if self.cascade:
            self.cascade.in_board(self.board).validate(False)

        if and_save:
            self.__compute_notation()
            self.board.moves.register(self)

        self.__player_consequences = piece.player.verify_status(self.board)
        self.__opponent_consequences = piece.player.opponent_in(
            self.board
        ).verify_status(self.board)

        return True

    def unvalidate(self):
        if self.cascade:
            self.cascade.in_board(self.board).unvalidate()

        assert hash(
            self.board
        ) == self.__board_hash_after, "The movement can't be unvalidated because the board is not at the right position."

        # pylint: disable=unsubscriptable-object
        piece = self.with_promotion[0] if self.with_promotion else self.board.pieces.at(
            self.to_position
        ).first()
        assert piece is not None, "Cannot unvalidate the movement: no piece at the end position"

        piece.cancel_move(self)

        self.__board_hash_after =\
            self._computed_notation =\
            self.__player_consequences =\
            self.__opponent_consequences =\
            None

        return True

    def __compute_notation(self):
        """
              Compute the generated movement in the __computed_notation property.
              This method must be called **AFTER** the movement has been fully made.
              Warning: call this method only once : the computed notation will be relative to the board current pieces positions
        """
        assert hash(
            self.board
        ) == self.__board_hash_after, "The notation cannot be computed as the board is not valid."

        # pylint: disable=unsubscriptable-object
        piece = self.with_promotion[0] if self.with_promotion else (
            self.board.pieces.at(self.to_position).playable().first()
        )
        assert piece is not None, "The movement cannot be linked to the given board : no piece at the end position"

        if self.with_castling is not None:
            self._computed_notation = "0-0" + (
                "-0" if self.with_castling == 'queen' else ""
            )
            return

        piece.ghost = True

        # (x, y)
        use_helpers = [False, False]

        for other_piece in self.board.pieces.of(piece.player).type(type(piece)).exept(piece):
            if self.to_position in [m.to_position for m in other_piece.legal_movements()]:
                use_helpers[0] = (
                    piece.position.y == other_piece.position.y
                ) or use_helpers[0]

                use_helpers[1] = (
                    piece.position.x == other_piece.position.x
                ) or use_helpers[1]

            if use_helpers[0] and use_helpers[1]:
                break

        piece.ghost = False

        from chess.pieces.pawn import Pawn

        self._computed_notation = (
            "" if isinstance(piece, Pawn) else f"{piece} "
        ) + (
            self.from_position.x if use_helpers[0] else ""
        ) + (
            self.from_position.y if use_helpers[1] else ""
        ) + (
            "x" if self.with_piece_eaten else ""
        ) + (
            str(self.to_position)
        ) + (
            self.with_promotion[1].NOTATION.upper()
            if self.with_promotion else ""
        ) + (
            "#" if self.__opponent_consequences.is_check_mate else
            "+" if self.__opponent_consequences.is_checked else ""
        ) if self.__opponent_consequences else ""
