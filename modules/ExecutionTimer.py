#!/usr/bin/env python3
"""ExecutionTimer.py - A reusable class to measure execution time"""

from time import time


class ExecutionTimer:
    """Class for timing the execution of a block of code."""

    def __init__(self):
        self.start_time = 0
        self.end_time = 0
        self.execution_time = 0

    def __enter__(self):
        """Context manager method to start the timer."""
        self.start_time = time()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.end_time = time()
        self.execution_time = self.end_time - self.start_time
        print(f"\n\033[34mExecution time: {str(self)}\033[0m")

    def __format__(self, format_spec: str, /) -> str:
        if format_spec == "r":
            return repr(self)
        else:
            return self.__str__()

    def __str__(self) -> str:
        """Convert result from seconds to hours, minutes, seconds, and/or milliseconds"""
        if self.execution_time < 1:
            return f"{round(self.execution_time * 1000)} ms"
        if self.execution_time >= 1 and self.execution_time < 60:
            return f"{round(self.execution_time)} s"
        if self.execution_time >= 60 and self.execution_time < 3600:
            minutes = round(self.execution_time / 60)
            self.execution_time = round(self.execution_time % 60)
            return f"{minutes} minutes, {self.execution_time} seconds"
        else:
            hours = round(self.execution_time / 3600)
            self.execution_time = round((self.execution_time % 3600) / 60)
            return f"{hours} hours, {self.execution_time} minutes"

    def __repr__(self):
        return f"{self.__class__.__name__}(execution_time={self.execution_time})"
