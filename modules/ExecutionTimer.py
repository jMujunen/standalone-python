#!/usr/bin/env python3

# ExecutionTimer.py - A reusable class to measure execution time

import os
from time import time

class ExecutionTimer:
    def __enter__(self):
        """
        Context manager for measuring execution time.
        """
        self.start_time = time()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.end_time = time()
        self.execution_time = self.end_time - self.start_time
        print(f"Execution time: {round(self.execution_time, 6)} seconds")

if __name__ == "__main__":
    with ExecutionTimer():
        """
        Measure the time taken to execute the code within this block.
        """
        print('START')
        for root, _, filename in os.walk("/home/joona/"):
            """
            Recursively walk through the directory "/home/joona/" and print the filenames.
            """
            for file in filename:
                print(file)




