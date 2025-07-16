from chess.boards.normal import NormalBoard
from chess.game.game import ChessGame
from chess.players.physical import PhysicalPlayer


# Fool
board = NormalBoard()
whites = PhysicalPlayer(1)
blacks = PhysicalPlayer(-1)

game = ChessGame((whites, blacks), board)
game.setup_board()
game.start()

game.play("f3")
game.play("e6")
game.play("g4")
game.play("Qh4")

verifier = whites.verify_status(board).verify_for_check().verify_for_end_game()
assert verifier.is_check_mate
