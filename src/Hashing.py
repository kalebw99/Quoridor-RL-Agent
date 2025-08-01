import numpy as np
from itertools import accumulate

class HashUtils:
    def __init__(self):
        self.lower_size = 32

    def to_str(self, board_state):

        ret = f"{board_state.my_piece_pos[0]}{board_state.my_piece_pos[1]}{board_state.enemy_piece_pos[0]}{board_state.enemy_piece_pos[1]}"
        ret += f"{board_state.my_walls:02d}{board_state.enemy_walls:02d}"
        ret += np.apply_along_axis(lambda x: sum(map(chr, x)), 0, np.apply_along_axis(lambda x: accumulate(x, lambda y, z: y << 2 + (z if z >= 0 else 2)), 0, board_state.board))
    
    def key(self, board_state):
        return hash(self.to_str(board_state))
    
    def key_split(self, board_state):
        k = self.key(board_state)
        return (k & ((1 << self.lower_size) - 1), k >> self.lower_size)
