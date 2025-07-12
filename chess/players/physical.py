import sys
from typing import TYPE_CHECKING
from chess.movement.board_movement import BoardMovement
from chess.players._player import Player
from chess.position import Position

if TYPE_CHECKING:
    from chess.game.game import ChessGame


class PhysicalPlayer(Player):
    def get_move(self, game: 'ChessGame', msg: str = "") -> BoardMovement | str:
        if msg:
            msg += " - "

        wanted = input(msg + "Type your move >> ")
        if wanted.startswith(":"):
            return self.command(wanted[1:], game)

        validated = BoardMovement.decode(wanted, game.board, self)
        if not validated:
            return self.get_move(game, "Invalid move, please retry !")
        return validated.in_board(game.board)

    def command(self, command: str,  game: 'ChessGame') -> str:
        command, *args = command.split()
        match command:
            case "exit":
                game.stop()
                print("Merci d'avoir joué !")
                return sys.exit(0)
            case "cancel":
                movement = game.moves.undo_last()
                return f"{movement} vient d'être annulé !" if movement else "Il n'y a pas de movement à annuler"
            case "pause":
                game.pause()
                return "Tapez :resume pour reprendre la partie !"
            case "legals":
                try:
                    position = Position(args[0])
                    piece = game.board.pieces.at(position).first()
                    if piece is None:
                        return "Impossible d'afficher les mouvements légales : aucune pièce sur la case demandée."

                    moves = piece.legal_movements(game.board)
                    if moves:
                        for move in moves:
                            print(move.to_position, end="; ")
                        print()
                    else:
                        print("Cette pièce ne peut pas bouger.")
                    input()
                    return ""

                except AssertionError as err:
                    return str(err.args[0])

        return "La commande n'est pas valide."
