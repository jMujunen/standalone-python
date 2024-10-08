from collections.abc import Callable, Generator, Iterable
from concurrent.futures import ThreadPoolExecutor, as_completed

from ProgressBar import ProgressBar


class Pool:
    """A helper class to manage a thread pool for executing tasks concurrently.

    ### Attributes:
        - `num_threads (int)`: The number of threads to use in the thread pool.
    """

    def __init__(self, num_threads=20):
        """Initialize the thread pool with a specified number of threads."""
        self.num_threads = num_threads

    def execute(
        self,
        callback_function: Callable,
        data_source: Iterable,
        progress_bar=True,
        *args,
        **kwargs,
    ) -> Generator:
        """Execute a callable function concurrently for each item in the data source.

        ### Parameters:
        --------------
            - `callback_function (Callable)`: The function to be executed for each item in the data source.
            - `data_source (Iterable)`: An iterable containing the data to be processed by the callback function.
            - `progress_bar (bool, optional)`: If True, a progress bar will be displayed. Default is True.
            - `*args` | `**kwarrgs`: Additional arguments to pass to the callback function.

        ### Returns:
        --------------
            - `Generator` that yields results from the callback function executions.

        ### Notes:
        ------------
            - If progress_bar is True and data_source is not a list or tuple, it will be converted to a list.
            - The execution of tasks is done concurrently using ThreadPoolExecutor.
            - Results are yielded as they are completed.
            - Exceptions encountered during task execution are caught and printed.
        """
        if progress_bar and isinstance(data_source, Generator):
            raise ValueError("Data source cannot be a generator when progress_bar=True")
        if progress_bar:
            progress_bar = ProgressBar(len(data_source))  # type: ignore
            with ThreadPoolExecutor(max_workers=self.num_threads) as executor:
                futures = [
                    executor.submit(callback_function, item, *args, **kwargs)
                    for item in data_source
                ]
                for future in as_completed(futures):
                    try:
                        yield future.result()
                    except Exception as exc:
                        print(f"\nException: {exc!r}")
                    finally:
                        progress_bar.increment()

        else:
            with ThreadPoolExecutor(max_workers=self.num_threads) as executor:
                futures = [executor.submit(callback_function, item, *args) for item in data_source]
                for future in as_completed(futures):
                    try:
                        result = future.result()
                        if result:
                            yield result
                    except Exception as exc:
                        print(f"\nException: {exc!r}")
