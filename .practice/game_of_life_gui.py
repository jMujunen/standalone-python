#!/usr/bin/env python3


import numpy as np
import matplotlib.pyplot as plt

BOARD_SIZE = 50

# Define the initial board with random values
board = np.random.choice([0, 1], size=(BOARD_SIZE, BOARD_SIZE))

# Define the rules for the Game of Life


def rules(board):
    new_board = board.copy()
    for x in range(BOARD_SIZE):
        for y in range(BOARD_SIZE):
            live_neighbors = (
                np.sum(
                    board[
                        max(0, x - 1) : min(BOARD_SIZE, x + 2),
                        max(0, y - 1) : min(BOARD_SIZE, y + 2),
                    ]
                )
                - board[x, y]
            )
            if board[x, y] == 1 and (live_neighbors < 2 or live_neighbors > 3):
                new_board[x, y] = 0
            elif board[x, y] == 0 and live_neighbors == 3:
                new_board[x, y] = 1
    return new_board


# Display the Game of Life simulation
fig, ax = plt.subplots()
img = ax.imshow(board, cmap="Greys")

for _generation in range(100):
    board = rules(board)
    img.set_data(board)
    plt.pause(0.2)

plt.show()
