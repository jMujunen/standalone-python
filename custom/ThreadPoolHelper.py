from collections.abc import Callable, Generator, Iterable
from typing import Any
from concurrent.futures import ThreadPoolExecutor, as_completed

from ProgressBar import ProgressBar


class Pool:
    """A helper class to manage a thread pool for executing tasks concurrently.

    ### Attributes:
        - `num_threads (int)`: The number of threads to use in the thread pool.
    """

    def __init__(self, num_threads=20, suppress_exceptions=False):
        """Initialize the thread pool with a specified number of threads."""
        self.num_threads = num_threads
        self.suppress_exceptions = suppress_exceptions

    def execute(
        self,
        function: Callable,
        data_source: Iterable[Any],
        progress_bar=True,
        *args,
        **kwargs,
    ) -> Generator[Any, None, None]:
        """Execute a callable function concurrently for each item in the data source.

        ### Parameters:
        --------------
            - `function (Callable)`: The function to be executed for each item in the data source.
            - `data_source (Iterable)`: An iterable containing the data to be processed by the specified function.
            - `progress_bar (bool, optional)`: If True, a progress bar will be displayed. Default is True.
            - `*args` | `**kwargs`: Additional arguments to pass to the specified function.

        ### Returns:
        --------------
            - `Generator` that yields results from the specified function executions.

        ### Notes:
        ------------
            - If progress_bar is True and data_source is not a list or tuple, it will be converted to a list.
            - The execution of tasks is done concurrently using ThreadPoolExecutor.
            - Results are yielded as they are completed.
            - Exceptions encountered during task execution are caught and printed.
        """
        if isinstance(data_source, Generator):
            # Convert generators to lists as calling `len` on a generator depletes it
            data_source = list(data_source)

        with (
            ThreadPoolExecutor(max_workers=self.num_threads) as executor,
            ProgressBar(len(data_source)) as pb,
        ):
            futures = [executor.submit(function, item, *args, **kwargs) for item in data_source]
            for future in as_completed(futures):
                try:
                    result = future.result()
                    yield result
                except StopIteration:
                    break
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    if not self.suppress_exceptions:
                        print(
                            f"\n\033[31mThreadpool Exception: {e!r} {function.__name__} {function.__module__}\033[0m"
                        )
                if progress_bar:
                    pb.increment()

        yield from ()
        print()
