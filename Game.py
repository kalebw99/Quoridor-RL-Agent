import copy
import heapq
import numpy as np
import matplotlib.pyplot as plt

from BoardState import BoardState

class Game:
        
    def __init__(self, init_state = None):
        self.board_state = init_state if init_state else BoardState()
        self.movable_area_graph = np.fromfunction(self.initialize_movable_area_graph, (9, 9, 4), dtype=object)
        self.my_path_to_exit = []
        self.enemy_path_to_exit = []
        self.prev_moves = []
        self.winner = 0
        self.turn_count = 0
        self.players = [None] * 2

    def register_player(self, player, isPlayerOne):
        self.players[0 if isPlayerOne else 1] = player

    def player_turn(self):
        self.players[self.turn_count % 2].on_player_turn()

    def get_all_moves(self):
        ret = self.get_all_wall_moves()
        ret.extend(self.get_all_piece_moves())
        return ret
    
    def get_all_wall_moves(self):

        moves = []
        if self.board_state.my_walls == 0:
            return moves
        for i in range(8):
            for j in range(8):
                if self.board_state.board[i, j] == 0:
                    if self.board_state.valid_wall_spots[i, j] >= 0:
                        candidate = (1, i, j)
                        if (tmp := self.validate_candidate(candidate))[0]:
                            moves.append(candidate + (tmp[1],))
                    if self.board_state.valid_wall_spots[i, j] <= 0:
                        candidate = (-1, i, j)
                        if (tmp := self.validate_candidate(candidate))[0]:
                            moves.append(candidate + (tmp[1],))
        return moves

    def get_all_piece_moves(self):
        moves = []

        move, blockers = self.board_state.left_piece_move(self.board_state.my_piece_pos)
        if self.piece_move_valid(move, blockers):
            moves.append((0, move[0], move[1]))

        move, blockers = self.board_state.right_piece_move(self.board_state.my_piece_pos)
        if self.piece_move_valid(move, blockers):
            moves.append((0, move[0], move[1]))

        move, blockers = self.board_state.down_piece_move(self.board_state.my_piece_pos)
        if self.piece_move_valid(move, blockers):
            moves.append((0, move[0], move[1]))
        
        move, blockers = self.board_state.up_piece_move(self.board_state.my_piece_pos)
        if self.piece_move_valid(move, blockers):
            moves.append((0, move[0], move[1]))

        dx = self.board_state.enemy_piece_pos[0] - self.board_state.my_piece_pos[0]
        dy = self.board_state.enemy_piece_pos[1] - self.board_state.my_piece_pos[1]
        if abs(dx) + abs(dy) != 1:
            return moves
        
        if abs(dx) == 1:
            move, blockers = self.board_state.horizontal_jump_piece_move(self.board_state.my_piece_pos, dx)
            if self.piece_move_valid(move, blockers):
                moves.append((0, move[0], move[1]))
            else:
                move, blockers = self.board_state.horizontal_down_piece_move(self.board_state.my_piece_pos, dx)
                if self.piece_move_valid(move, blockers):
                    moves.append((0, move[0], move[1]))
                move, blockers = self.board_state.horizontal_up_piece_move(self.board_state.my_piece_pos, dx)
                if self.piece_move_valid(move, blockers):
                    moves.append((0, move[0], move[1]))

        if abs(dy) == 1:
            move, blockers = self.board_state.vertical_jump_piece_move(self.board_state.my_piece_pos, dy)
            if self.piece_move_valid(move, blockers):
                moves.append((0, move[0], move[1]))
            else:
                move, blockers = self.board_state.vertical_left_piece_move(self.board_state.my_piece_pos, dy)
                if self.piece_move_valid(move, blockers):
                    moves.append((0, move[0], move[1]))
                move, blockers = self.board_state.vertical_right_piece_move(self.board_state.my_piece_pos, dy)
                if self.piece_move_valid(move, blockers):
                    moves.append((0, move[0], move[1]))
        return moves

    def flip_board(self):
        self.board_state.flip_board()
        self.my_path_to_exit, self.enemy_path_to_exit = [(8 - p[0], 8 - p[1]) for p in self.enemy_path_to_exit], [(8 - p[0], 8 - p[1]) for p in self.my_path_to_exit]
        self.movable_area_graph = np.flip(self.movable_area_graph)
        self.movable_area_graph['x'] = np.where(self.movable_area_graph['x'] != -1, 8 - self.movable_area_graph['x'], -1)
        self.movable_area_graph['y'] = np.where(self.movable_area_graph['y'] != -1, 8 - self.movable_area_graph['y'], -1)
        self.winner *= -1

    def initialize_movable_area_graph(self, i, j, k):
        ij_tuples = list(zip(i[:, :, 0].flatten(), j[:, :, 0].flatten()))
        ret = np.stack([
                    np.array([(x + 1, y) if x < 8 else (-1, -1) for x, y in ij_tuples], dtype=[("x","<i4"),("y","<i4")]).reshape(9, 9), #right move
                    np.array([(x, y - 1) if y > 0 else (-1, -1) for x, y in ij_tuples], dtype=[("x","<i4"),("y","<i4")]).reshape(9, 9), #down move
                    np.array([(x, y + 1) if y < 8 else (-1, -1) for x, y in ij_tuples], dtype=[("x","<i4"),("y","<i4")]).reshape(9, 9), #up move
                    np.array([(x - 1, y) if x > 0 else (-1, -1) for x, y in ij_tuples], dtype=[("x","<i4"),("y","<i4")]).reshape(9, 9)  #left move
                    ], axis=-1)
        return ret

    def backtrack(self, from_pos, to_pos, visited):
        ret = []
        tmp = from_pos
        while tmp != to_pos:
            ret.append(tmp)
            tmp = tuple(visited[tmp])
        ret.append(to_pos)
        return ret[::-1]
    
    def path_to_exit(self, start_pos, is_enemy=False):
        horizon = []
        visited = np.array(list(zip(np.full((9, 9), -1).flatten(), np.full((9, 9), -1).flatten())), dtype=[("x","<i4"),("y","<i4")]).reshape(9, 9)
        heapq.heappush(horizon, (8 - start_pos[1], start_pos))
        visited[start_pos] = start_pos
        while horizon:
            prio, pos = heapq.heappop(horizon)
            for neighbor in self.movable_area_graph[pos]:
                neighbor = tuple(neighbor)
                if neighbor != (-1, -1) and tuple(visited[neighbor]) == (-1, -1):
                    visited[neighbor] = pos
                    if (not is_enemy and neighbor[1] == 8) or (is_enemy and neighbor[1] == 0):
                        return self.backtrack(neighbor, start_pos, visited)
                    heapq.heappush(horizon, (prio + pos[1] + 1 - neighbor[1], neighbor))
        return []

    def piece_moves_blocked(self, wall_move):
        if wall_move[0] == 1:
            return [[(wall_move[1], wall_move[2]), (wall_move[1] + 1, wall_move[2])],
                    [(wall_move[1], wall_move[2] + 1), (wall_move[1] + 1, wall_move[2] + 1)],
                    [(wall_move[1] + 1, wall_move[2]), (wall_move[1], wall_move[2])],
                    [(wall_move[1] + 1, wall_move[2] + 1), (wall_move[1], wall_move[2] + 1)]]
        else: #wall_move[0] == -1
            return [[(wall_move[1], wall_move[2]), (wall_move[1], wall_move[2] + 1)],
                    [(wall_move[1] + 1, wall_move[2]), (wall_move[1] + 1, wall_move[2] + 1)],
                    [(wall_move[1], wall_move[2] + 1), (wall_move[1], wall_move[2])],
                    [(wall_move[1] + 1, wall_move[2] + 1), (wall_move[1] + 1, wall_move[2])]]
            

    def validate_candidate(self, candidate):
        blocked_moves = self.piece_moves_blocked(candidate)
        if self.my_path_to_exit and\
                self.enemy_path_to_exit and\
                all([all([self.my_path_to_exit[k:k+2] != blocked_moves[l] for k in range(len(self.my_path_to_exit) - 1)]) for l in range(4)]) and\
                all([all([self.enemy_path_to_exit[k:k+2] != blocked_moves[l] for k in range(len(self.enemy_path_to_exit) - 1)]) for l in range(4)]):
            return (True, True)
        elif (tmp := self.peek_move(candidate)).path_to_exit(self.enemy_piece_pos, is_enemy=True)\
                and tmp.path_to_exit(self.my_piece_pos):
            return (True, False)
        return (False, False)
    
    def update_movable_area_graph(self, move):
        for blocked_move in self.piece_moves_blocked(move[:3]):
            y_filter, x_filter, _ = np.meshgrid(np.arange(9), np.arange(9), np.arange(4))
            self.movable_area_graph[(x_filter == blocked_move[0][0]) & 
                                    (y_filter == blocked_move[0][1]) &
                                    (self.movable_area_graph['x'] == blocked_move[1][0]) &
                                    (self.movable_area_graph['y'] == blocked_move[1][1])
                                    ] = (-1, -1)
            
    def make_move(self, move):
        #move[0]: piece (0), vert wall (1), or horiz wall (-1)
        #move[1]: piece or wall x position
        #move[2]: piece or wall y position
        #move[3] (wall moves only): current exit path valid
        match move[0]:
            case 0: #piece move
                self.board_state.my_piece_pos = (move[1:3])
                self.my_path_to_exit.insert(0, self.board_state.my_piece_pos)
            case 1:
                self.board_state.board[move[1:3]] = 1
                self.update_movable_area_graph(move)
                if move[2] - 1 >= 0:
                    self.board_state.valid_wall_spots[move[1], move[2] - 1] = -1
                if move[2] + 1 <= 7:
                    self.board_state.valid_wall_spots[move[1], move[2] + 1] = -1
                if len(move) < 4 or not move[3]:
                    self.my_path_to_exit = self.path_to_exit(self.board_state.my_piece_pos)
                    self.enemy_path_to_exit = self.path_to_exit(self.board_state.enemy_piece_pos, is_enemy=True)
            case -1:
                self.board_state.board[move[1:3]] = -1
                self.update_movable_area_graph(move)
                if move[1] - 1 >= 0:
                    self.board_state.valid_wall_spots[move[1] - 1, move[2]] = 1
                if move[1] + 1 <= 7:
                    self.board_state.valid_wall_spots[move[1] + 1, move[2]] = 1
                if len(move) < 4 or not move[3]:
                    self.my_path_to_exit = self.path_to_exit(self.board_state.my_piece_pos)
                    self.enemy_path_to_exit = self.path_to_exit(self.board_state.enemy_piece_pos, is_enemy=True)
        self.board_state.my_walls -= 1
        self.prev_moves.append(move)
        self.turn_count += 1
        self.flip_board()

    def peek_move(self, move):

        new_game = copy.deepcopy(self)
        new_game.make_move(move)
        new_game.flip_board()
        return new_game

    def piece_move_valid(self, move, blockers):
        return all(i in range(9) for i in move)\
                and all(any(i not in range(8) for i in blocker[0]) or\
                        all(self.board_state.board[blocker[0]] != p for p in blocker[1])\
                        for blocker in blockers.items())\
                and self.board_state.enemy_piece_pos != move

    def get_image_of_pos(self, board=None):
        board = board if board else self.board_state.board
        plt.style.use('_mpl-gallery-nogrid')


        image = np.zeros((53, 53, 3), dtype=np.uint8)
        for i in range(5, 53, 6):
            image[i, :, :] = 255
            image[:, i, :] = 255

        for i in range(8):
            for j in range(8):
                if self.board_state.board[i, j] == 1:
                    image[((7-j)*6+1):((7-j)*6+10), (i*6+4):(i*6+7), :] = 128
                elif self.board_state.board[i, j] == -1:
                    image[((7-j)*6+4):((7-j)*6+7), (i*6+1):(i*6+10), :] = 128
        
        image[((8-self.board_state.my_piece_pos[1])*6+1):((8-self.board_state.my_piece_pos[1])*6+4), 
              (self.board_state.my_piece_pos[0]*6+1):(self.board_state.my_piece_pos[0]*6+4), 0] = 255
        image[((8-self.board_state.enemy_piece_pos[1])*6+1):((8-self.board_state.enemy_piece_pos[1])*6+4), 
              (self.board_state.enemy_piece_pos[0]*6+1):(self.board_state.enemy_piece_pos[0]*6+4), 1] = 255

        return image
    
    def run(self):
        while self.winner == 0:
            self.player_turn()