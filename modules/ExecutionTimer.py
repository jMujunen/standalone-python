#!/usr/bin/env python3

# ExecutionTimer.py - A reusable class to measure execution time

import os
from time import time


class ExecutionTimer:
    def __init__(self):
        pass

    def __enter__(self):
        """
        Context manager for measuring execution time.
        """
        self.start_time = time()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.end_time = time()
        self.execution_time = self.end_time - self.start_time
        print(
            f"\n\033[34mExecution time: {self.format_execution_time(self.execution_time)}\033[0m"
        )

    def format_execution_time(self, seconds):
        # Format the execution time in hours, minutes, seconds, and milliseconds
        if seconds < 1:
            return f"{round(seconds * 1000)} milliseconds"
        if seconds >= 1 and seconds < 60:
            return f"{round(seconds)} seconds"
        elif seconds >= 60 and seconds < 3600:
            minutes = round(seconds / 60)
            seconds = round(seconds % 60)
            return f"{minutes} minutes, {seconds} seconds"
        else:
            hours = round(seconds / 3600)
            minutes = round((seconds % 3600) / 60)
            seconds = round((seconds % 3600) % 60)
            return f"{hours} hours"


if __name__ == "__main__":
    with ExecutionTimer():
        """
        Measure the time taken to execute the code within this block.
        """
        print("START")
        for root, _, filename in os.walk("/home/joona/"):
            """
            Recursively walk through the directory "/home/joona/" and print the filenames.
            """
            for file in filename:
                print(file)
