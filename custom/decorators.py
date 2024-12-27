from typing import Any
from collections.abc import Callable
import datetime
from ExecutionTimer import ExecutionTimer


def exectimer(func: Callable[..., Any], /) -> Callable[..., Any]:
    """Measure execution time of a function."""

    def wrapper(*args, **kwargs) -> Any:
        with ExecutionTimer(print_on_exit=False) as timer:
            result = func(*args, **kwargs)
        msg = f"{func.__name__} took {timer.execution_time:.4f} seconds to execute."
        print(msg)
        return result

    return wrapper

import time

def clstimer(cls):
    """
    Class decorator to measure the execution time of all methods in the class.

    The execution time is printed for each method.
    Note that this decorator will not work if used with abstract base classes (ABC).

    Usage:
        @timer
        class MyClass:
            def __init__(self, name):
                self.name = name

            def say_hello(self):
                print(f"Hello {self.name}!")

    This will measure and print the execution time of both __init__ and say_hello methods.
    """

    # Wrap each method in a timer function
    for attr_name, attr_value in cls.__dict__.items():
        if callable(attr_value):
            setattr(cls, attr_name, _timer_wrapper(attr_value))

    return cls

def _timer_wrapper(func):
    """
    Timer wrapper that measures the execution time of a function.

    Args:
        func (callable): The function to be timed.

    Returns:
        wrapped_func: The decorated function.
    """

    def wrapped_func(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()

        # Print the execution time
        print(f"{func.__name__} executed in {end_time - start_time:.6f}s")

        return result

    return wrapped_func
