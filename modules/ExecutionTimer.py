"""ExecutionTimer.py - A reusable class to measure execution time."""

from time import time


class ExecutionTimer:
    """Class for timing the execution of a block of code."""

    def __init__(self, print_on_exit=True) -> None:
        self.start_time = 0
        self.end_time = 0
        self.execution_time = 0
        self.print_on_exit = print_on_exit

    def __enter__(self):
        """Context manager method to start the timer."""
        self.start_time = time()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.end_time = time()
        self.execution_time = self.end_time - self.start_time
        if self.print_on_exit:
            print(f"\n\033[34mExecution time: {self!s}\033[0m")

    def __format__(self, format_spec: str, /) -> str:
        match format_spec.lower():
            case "r":
                return repr(self)
            case "f":
                return f"{self.execution_time}"
        return self.__str__()

    def __str__(self) -> str:
        """Convert result from seconds to hours, minutes, seconds, and/or milliseconds."""
        if self.execution_time < 1:
            return f"{round(self.execution_time * 1000)}ms"
        if self.execution_time >= 1 and self.execution_time < 60:
            return f"{(self.execution_time):.2f}s"
        if self.execution_time >= 60 and self.execution_time < 3600:
            minutes = round(self.execution_time / 60)
            self.execution_time = round(self.execution_time % 60)
            return f"{minutes}min, {self.execution_time}s"
        hours = round(self.execution_time / 3600)
        self.execution_time = round((self.execution_time % 3600) / 60)
        return f"{hours}h, {self.execution_time}min"

    def __repr__(self) -> str:
        return f"CompletedTimer({self.execution_time})"
