import datetime
from collections.abc import Callable, Generator, Iterable
from concurrent.futures import ThreadPoolExecutor, as_completed

# DEBUG: Remove after
from fsutils import Dir
from fsutils.ImageFile import Img, imagehash

from ProgressBar import ProgressBar


class Pool(ProgressBar):
    def __init__(self, num_threads=20):
        self.num_threads = num_threads

    def execute(
        self, callback_function: Callable, data_source: Iterable, *args, progress_bar=True
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
                        print(f"Generated an exception: {exc}")
                    finally:
                        if progress_bar:
                            pb.increment()


# Usage example
if __name__ == "__main__":
    images = Dir("/home/joona/Pictures/RuneLite").images

    def extract_data(image: Img) -> tuple[datetime.datetime, imagehash.ImageHash | None]:
        for tag in image.tags:
            name, val = tag
            print(f"{name:<30} {val:<10}")
        h = image.calculate_hash()
        date = image.capture_date
        return date, h

    thread_pool_helper = Pool()
    for result in thread_pool_helper.execute(extract_data, images):
        print("{:<30}{:<30}".format(*result))
