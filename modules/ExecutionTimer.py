"""ExecutionTimer.py - A reusable class to measure execution time."""

from enum import Enum
from time import time


class TimeUnits(Enum):
    S = 1
    M = 60
    H = 60**2
    D = 24 * 60**2


class ExecutionTimer:
    """Class for timing the execution of a block of code."""

    start_time: float = 0.0
    end_time: float = 0.0
    execution_time: float = 0.0

    def __init__(self, print_on_exit=True) -> None:
        """Initialize the instance."""
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
        return "Depreciated Function"

    #     match format_spec.lower():
    #         case "r":
    #             return repr(self)
    #         case "f":
    #             return f"{self.execution_time}"
    #     return self.__str__()

    def __str__(self) -> str:
        """Convert result from seconds to hours, minutes, seconds, and/or milliseconds."""
        for unit in TimeUnits:
            if self.execution_time < TimeUnits.M.value:
                return f"{self.execution_time:.2f}{unit.name.lower()}"
            self.execution_time /= TimeUnits.M.value

        return f"{self.execution_time / 1024:.2f} {TimeUnits.H.name.lower()}"
