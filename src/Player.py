import time
from Game import Game
from BoardState import BoardState
from TranspositionTable import TranspositionTable

class BasePlayer:
    def __init__(self, game, isPlayerOne):
        self.register(game, isPlayerOne)

    def register(self, game, isPlayerOne):
        self.game = game
        self.game.register_player(self, isPlayerOne)

    def on_player_turn(self):
        moves = self.game.get_all_moves()
        self.make_move(self.choose_move(moves))

    def make_move(self, move):
        self.game.make_move(move)

    def choose_move(self, moves):
        raise NotImplementedError

class RLPlayer(BasePlayer):
    def __init__(self, game, isPlayerOne):
        super().__init__(self, game, isPlayerOne)
        self.transposition_table = TranspositionTable()

    def choose_move(self, moves):
        alpha = float('-inf')
        beta = float('inf')
        depth = 0
        tstart = time.now()
        max_time = 300
        while time.now() - tstart <= max_time:
            for move in moves:
                self.alpha_beta_eval(self.game, alpha, beta, depth, True)
            depth += 1

    def alpha_beta_eval(self, state, alpha, beta, maxDepth, maximizing):
        pass
