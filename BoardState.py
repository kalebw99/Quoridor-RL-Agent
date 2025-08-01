import copy
import heapq
import numpy as np

class BoardState:
    def __init__(self):
        self.board = np.zeros((8, 8), dtype=np.int8)
        self.valid_wall_spots = np.zeros((8, 8), dtype=np.int8)
        self.my_piece_pos = (4, 0)
        self.enemy_piece_pos = (4, 8)
        self.my_walls = 10
        self.enemy_walls = 10
        
    def down_piece_move(self, pos):
        move = (pos[0], pos[1] - 1) # down
        blockers = {(pos[0] - 1, pos[1] - 1): (-1,), 
                    (pos[0], pos[1] - 1): (-1,)}
        return move, blockers
    
    def up_piece_move(self, pos):
        move = (pos[0], pos[1] + 1) # up
        blockers = {(pos[0] - 1, pos[1]): (-1,), 
                    (pos[0], pos[1]): (-1,)}
        return move, blockers
    
    def left_piece_move(self, pos):
        move = (pos[0] - 1, pos[1]) # left
        blockers = {(pos[0] - 1, pos[1] - 1): (1,),
                    (pos[0] - 1, pos[1]): (1,)}
        return move, blockers
        
    def right_piece_move(self, pos):
        move = (pos[0] + 1, pos[1]) # right
        blockers = {(pos[0], pos[1] - 1): (1,),
                    (pos[0], pos[1]): (1,)}
        return move, blockers
        
    def horizontal_jump_piece_move(self, pos, dx):
        move = (pos[0] + dx * 2, pos[1]) # left or right jump
        blockers = {(pos[0] + (dx - 1) // 2, pos[1] - 1): (1,),
                    (pos[0] + (dx - 1) // 2, pos[1]): (1,),
                    (pos[0] + (3 * dx - 1) // 2, pos[1] - 1): (1,),
                    (pos[0] + (3 * dx - 1) // 2, pos[1]): (1,)}
        return move, blockers
        
    def vertical_jump_piece_move(self, pos, dy):
        move = (pos[0], pos[1] + dy * 2) # up or down jump
        blockers = {(pos[0] - 1, pos[1] + (dy - 1) // 2): (-1,),
                    (pos[0], pos[1] + (dy - 1) // 2): (-1,),
                    (pos[0] - 1, pos[1] + (3 * dy - 1) // 2): (-1,),
                    (pos[0], pos[1] + (3 * dy - 1) // 2): (-1,)}
        return move, blockers
    
    def horizontal_down_piece_move(self, pos, dx):
        move = (pos[0] + dx, pos[1] - 1)
        blockers = {(pos[0] + (dx - 1) // 2, pos[1] - 1): (-1, 1), 
                    (pos[0] + (dx - 1) // 2, pos[1]): (1,),
                    (pos[0] + (3 * dx - 1) // 2, pos[1] - 1): (-1,)}
        return move, blockers
    
    def horizontal_up_piece_move(self, pos, dx):
        move = (pos[0] + dx, pos[1] + 1)
        blockers = {(pos[0] + (dx - 1) // 2, pos[1] - 1): (1,), 
                    (pos[0] + (dx - 1) // 2, pos[1]): (-1, 1),
                    (pos[0] + (3 * dx - 1) // 2, pos[1]): (-1,)}
        return move, blockers
    
    def vertical_left_piece_move(self, pos, dy):
        move = (pos[0] - 1, pos[1] + dy)
        blockers = {(pos[0] - 1, pos[1] + (dy - 1) // 2): (-1, 1), 
                    (pos[0], pos[1] + (dy - 1) // 2): (-1,),
                    (pos[0] - 1, pos[1] + (3 * dy - 1) // 2): (1,)}
        return move, blockers
    
    def vertical_right_piece_move(self, pos, dy):
        move = (pos[0] + 1, pos[1] + dy)
        blockers = {(pos[0] - 1, pos[1] + (dy - 1) // 2): (-1,), 
                    (pos[0], pos[1] + (dy - 1) // 2): (-1, 1),
                    (pos[0], pos[1] + (3 * dy - 1) // 2): (1,)}
        return move, blockers

    def flip_board(self):
        self.board = np.flip(self.board)
        self.valid_wall_spots = np.flip(self.valid_wall_spots)
        self.my_piece_pos, self.enemy_piece_pos = (8 - self.enemy_piece_pos[0], 8 - self.enemy_piece_pos[1]), (8 - self.my_piece_pos[0], 8 - self.my_piece_pos[1])
        #print("Before flip:\nMine: " + str(self.my_piece_pos) + "\nTheirs: " + str(self.enemy_piece_pos))
        self.my_walls, self.enemy_walls = self.enemy_walls, self.my_walls