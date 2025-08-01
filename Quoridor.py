import matplotlib.pyplot as plt
import matplotlib.animation as animation
from random import randrange

from Game import Game
from Hashing import HashUtils

def main():
    g = Game()
    g.make_move((0, 4, 1))
    g.make_move((0, 4, 1))
    g.make_move((0, 4, 2))
    g.make_move((0, 4, 2))
    g.make_move((0, 4, 3))
    g.make_move((0, 4, 3))
    g.make_move((0, 4, 4))
    g.make_move((0, 3, 3))
    g.make_move((0, 4, 5))
    g.make_move((1, 4, 3))
    g.make_move((-1, 4, 3))
    HashUtils().to_str(g.board_state)

    num_moves = 10
    '''for i in range(num_moves):
        p = g.get_all_piece_moves()
        w = g.get_all_wall_moves()
        move = w[randrange(len(w))] if randrange(2) == 0 and len(w) > 0 else p[randrange(len(p))]
        g.make_move(move)
        g.flip_board()
        #print("board: " + str(g.board.tolist()))
    g.flip_board()
    #print(g.get_all_moves())'''

    cur_pos = g.get_image_of_pos()

    future_moves = g.get_all_piece_moves()
    next_pos = []
    for move in future_moves:
        next_pos.append(g.peek_move(move).get_image_of_pos())

    fig = plt.figure()
    ax = fig.subplots(2)
    ax[0].imshow(cur_pos)
    ims = []
    for i in range(len(next_pos)):
        im = ax[1].imshow(next_pos[i], animated=(i == 0))
        ims.append([im])

    ani = animation.ArtistAnimation(fig, ims, blit=True, interval=350)
    plt.show()
        
  
if __name__ == '__main__':
    main()