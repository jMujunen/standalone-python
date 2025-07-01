import os
from collections.abc import Callable, Generator, Iterable, Sized
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Concatenate, ParamSpec, TypeVar

from tqdm import tqdm

DataT = TypeVar("DataT")
P = ParamSpec("P")
R = TypeVar("R")


class Pool:
    """A helper class to manage a thread pool for executing tasks concurrently.

    Attributes:
        suppress_exceptions (bool): If True, exceptions raised by worker functions will be suppressed.
    """

    def __init__(self, *, suppress_exceptions: bool = False):
        """Initialize the thread pool with a specified number of threads."""
        self.suppress_exceptions = suppress_exceptions

    def execute(
        self,
        function: Callable[Concatenate[DataT, P], R],
        data_source: Iterable[Any],
        /,
        progress_bar: bool = True,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> Generator[R]:
        """Execute a callable function concurrently for each item in the data source.

        ### Parameters:
        --------------
            - `function (Callable)`: The function to be executed for each item in the data source.
            - `data_source (Iterable)`: An iterable containing the data to be processed by the specified function.
            - `progress_bar (bool): If False, no progress bar will be displayed.
            - `*args` | `**kwargs`: Additional arguments to pass to the specified function.

        ### Returns:
        --------------
            - `Generator` that yields results from the specified function executions.

        Note: If data_source a generator, it will be converted to a list.
        """
        if not isinstance(data_source, Sized):
            # Convert generators to lists as calling `len` on a generator depletes it
            data_source = list(data_source)

        exceptions = []
        template = "\033[31m{}: \033[0m{name}({item}, {args}, {kwargs})"

        with ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(function, item, *args, **kwargs): item
                for item in data_source
            }

            with tqdm(total=len(data_source), disable=not progress_bar) as bar:
                for future in as_completed(futures):
                    try:
                        result = future.result()
                        yield result
                    except (StopIteration, KeyboardInterrupt):
                        break
                    except Exception as e:
                        item = futures[future]
                        details = {
                            "name": function.__name__,
                            "args": args,
                            "kwargs": kwargs,
                            "item": str(item),
                        }
                        e.__setattr__("details", details)
                        if not self.suppress_exceptions:
                            print(
                                f"\n{e!r}",
                                template.format(e.__class__.__name__, **details),
                            )

                        exceptions.append(e)

                    bar.update()
        yield from ()
