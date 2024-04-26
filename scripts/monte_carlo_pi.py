#!/usr/bin/env python3

# monte_carlo_pi.py - A Monte Carlo simulation to estimate the value of Pi

import random
import multiprocessing
from ExecutionTimer import ExecutionTimer

def monte_carlo_pi(iterations):
    inside_circle = 0
    for _ in range(iterations):
        x = random.random()
        y = random.random()
        if x**2 + y**2 <= 1:
            inside_circle += 1
    return (inside_circle / iterations) * 4

if __name__ == "__main__":
    

    num_iterations = 10**10
    num_processes = multiprocessing.cpu_count()

    with multiprocessing.Pool(processes=num_processes) as pool:
        results = pool.map(monte_carlo_pi, [num_iterations // num_processes] * num_processes)

    end_time = time.time()
    print(f"Estimated value of Pi: {sum(results) / num_processes}")
    print(f"Execution time: {end_time - start_time} seconds")