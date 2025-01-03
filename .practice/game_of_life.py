#!/usr/bin/env python3
import random
from time import sleep
import os

BOARD_SIZE = 40


def live_neighbors(board: list[list], x: int, y: int) -> int:
    """Calculate the number of live neighbors for a cell at (x, y)."""
    live_count = 0
    for i in range(-1, 2):
        for j in range(-1, 2):
            if i == 0 and j == 0:
                continue
            nx, ny = x + i, y + j
            if 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE:
                live_count += board[nx][ny]
    return live_count


def main():
    # # Define the initial board with random values
    board = [[random.randint(0, 1) for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
    # # Precompute live neighbors for each cell
    live_neighbors_cache = [[0 for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

    # Run the Game of Life for 1000 generations
    for generation in range(1000):
        new_board = [row[:] for row in board]  # Deep copy to avoid modifying during iteration

        for x in range(BOARD_SIZE):
            for y in range(BOARD_SIZE):
                if board[x][y] == 1:
                    live_neighbors_cache[x][y] -= 1
                else:
                    live_neighbors_cache[x][y] = live_neighbors(board, x, y)

                new_board[x][y] = rules(board, x, y, live_neighbors_cache[x][y])

        board = new_board

        # Print the current generation (without clearing the screen)
        for row in board:
            print(" ".join(["#" if cell == 1 else "." for cell in row]))
        sleep(0.1)


def rules(board, x: int, y: int, new_live_neighbor_count) -> int:
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
    if board[x][y] == 1 and live_neighbors in {2, 3}:
        return 1  # Any live cell with two or three live neighbors lives
    if board[x][y] == 1 and live_neighbors > 3:
        return 0  # Any live cell with more than three live neighbors dies
    if board[x][y] == 0 and live_neighbors == 3:
        return 1  # Any dead cell with exactly three live neighbors becomes a live cell
    return board[x][y]  # All other cells remain in their current state


if __name__ == "__main__":
    main()
