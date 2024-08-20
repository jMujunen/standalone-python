import datetime
from collections.abc import Callable, Generator, Iterable
from concurrent.futures import ThreadPoolExecutor, as_completed

from ProgressBar import ProgressBar


class Pool(ProgressBar):
    def __init__(self, num_threads=20):
        self.num_threads = num_threads

    def execute(
        self,
        callback_function: Callable,
        data_source: Iterable,
        *args,
        progress_bar=True,
    ) -> Generator:
        with ProgressBar(len(data_source)) as pb:
            with ThreadPoolExecutor(max_workers=self.num_threads) as executor:
                futures = [executor.submit(callback_function, item, *args) for item in data_source]
                for future in as_completed(futures):
                    try:
                        result = future.result()
                        if result:
                            yield result
                    except Exception as exc:
                        print(f"\nException: {exc!r}")
                    finally:
                        if progress_bar:
                            pb.increment()
