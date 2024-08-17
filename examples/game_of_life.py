#!/usr/bin/env python3

import random
from time import sleep
import os

BOARD_SIZE = 40

# Define the initial board with random values
board = [[random.randint(0, 1) for x in range(BOARD_SIZE)] for y in range(BOARD_SIZE)]

# Print the initial board
print("Initial Board:")
for row in board:
    print(" ".join(["#" if cell == 1 else "." for cell in row]))

# Define the rules for the Game of Life


def rules(board, x, y):
    # Count the number of live neighbors
    live_neighbors = 0
    for i in range(-1, 2):
        for j in range(-1, 2):
            if i == 0 and j == 0:
                continue
            if x + i < 0 or x + i >= BOARD_SIZE or y + j < 0 or y + j >= BOARD_SIZE:
                continue
            if board[x + i][y + j] == 1:
                live_neighbors += 1

    # Apply the rules
    if board[x][y] == 1 and live_neighbors < 2:
        return 0  # Any live cell with fewer than two live neighbors dies
    if board[x][y] == 1 and live_neighbors in [2, 3]:
        return 1  # Any live cell with two or three live neighbors lives
    if board[x][y] == 1 and live_neighbors > 3:
        return 0  # Any live cell with more than three live neighbors dies
    if board[x][y] == 0 and live_neighbors == 3:
        return 1  # Any dead cell with exactly three live neighbors becomes a live cell
    return board[x][y]  # All other cells remain in their current state


# Run the Game of Life for 10 generations
for _generation in range(1000):
    new_board = [[0 for x in range(BOARD_SIZE)] for y in range(BOARD_SIZE)]
    for x in range(BOARD_SIZE):
        for y in range(BOARD_SIZE):
            new_board[x][y] = rules(board, x, y)
    board = new_board

    # Print the current generation
    os.system("clear")
    for row in board:
        print(" ".join(["#" if cell == 1 else "." for cell in row]))
    sleep(0.1)
