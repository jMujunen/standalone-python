#!/usr/bin/env python3
"""ExecutionTimer.py - A reusable class to measure execution time"""

from time import time

# from ProgressBar import ProgressBar


class ExecutionTimer:
    """Execution Timer: Measure and display execution time for a block of code.

    Methods:
    --------
        - `fmttime` (seconds):  Format the execution time to
        hours, minutes, seconds, and milliseconds.
    """

    def __init__(self):
        # progress_bar: ProgressBar | None = None):
        self.start_time = 0
        self.end_time = 0
        self.execution_time = 0
        # self.progress_bar = progress_bar

    def __enter__(self):
        self.start_time = time()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # if self.progress_bar is not None:
        #     self.progress_bar.complete()
        #     print()
        self.end_time = time()
        self.execution_time = self.end_time - self.start_time
        print(f"\n\033[34mExecution time: {self.fmttime(self.execution_time)}\033[0m")

    def fmttime(self, seconds):
        """Convert result from seconds to hours, minutes, seconds, and/or milliseconds"""
        if seconds < 1:
            return f"{round(seconds * 1000)} milliseconds"
        if seconds >= 1 and seconds < 60:
            return f"{round(seconds)} seconds"
        if seconds >= 60 and seconds < 3600:
            minutes = round(seconds / 60)
            seconds = round(seconds % 60)
            return f"{minutes} minutes, {seconds} seconds"
