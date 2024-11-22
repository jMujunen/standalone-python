"""ExecutionTimer.py - A reusable class to measure execution time."""

from enum import Enum
from time import time


class TimeUnits(Enum):
    ms = 1e-3
    seconds = 1
    minutes = 60
    hours = 60**2
    days = 24 * 60**2


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

    # def __format__(self, format_spec: str, /) -> str:
    #     return "Depreciated Function"

    #     match format_spec.lower():
    #         case "r":
    #             return repr(self)
    #         case "f":
    #             return f"{self.execution_time}"
    #     return self.__str__()

    def __str__(self) -> str:
        """Convert result from seconds to hours, minutes, seconds, and/or milliseconds."""
        template = "{minutes}{major_unit}{seconds} {minor_unit}"
        time_seconds = self.execution_time
        for unit in TimeUnits:
            if time_seconds < TimeUnits.seconds.value:
                return template.format(
                    minutes="",
                    major_unit="",
                    seconds=f"{time_seconds/TimeUnits.ms.value:.0f}",
                    minor_unit=TimeUnits.ms.name,
                )
            if unit.name == "ms":
                continue
            time_seconds = time_seconds / unit.value
            if time_seconds < TimeUnits.minutes.value:
                return template.format(
                    minutes="",
                    major_unit="",
                    seconds=f"{time_seconds:.2f}",
                    minor_unit=unit.name,
                )
            if time_seconds < TimeUnits.hours.value:
                return template.format(
                    minutes="",
                    major_unit="",
                    seconds=f"{time_seconds:.0f}",
                    minor_unit=unit.name,
                )

            time_seconds /= TimeUnits.minutes.value

        return f"{time_seconds / 60/24:.2f} {TimeUnits.days.name.lower()}"
