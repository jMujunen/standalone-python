#!/usr/bin/env python3

import os
import sys
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor, as_completed

from ExecutionTimer import ExecutionTimer
from fsutils import Dir, File
from ProgressBar import ProgressBar
from size import Converter


def process_file(file: File) -> tuple[str, int] | None:
    try:
        return (file.path, file.size)
    except Exception:
        pass


def find_file_sizes(directory: Dir) -> tuple[OrderedDict[str, int], int]:
    total = 0
    file_mapping = OrderedDict()
    file_objects = directory.file_objects
    with ProgressBar(len(file_objects)) as progress:
        with ThreadPoolExecutor(20) as executor:
            futures = [executor.submit(process_file, file) for file in file_objects]
            for future in as_completed(futures):
                result = future.result()
                progress.increment()
                if result:
                    file_name, file_size = result
                    file_mapping[file_name] = file_size
                    total += file_size
    return file_mapping, total


def main(path: str) -> int:
    dictionary_result, total = find_file_sizes(Dir(path))
    # Print a formatted table of file sizes sorted from smallest to largest
    sorted_result = OrderedDict(sorted(dictionary_result.items(), key=lambda item: item[1]))
    print("\nFile Size")
    for file, size in sorted_result.items():
        relative_path = os.path.relpath(file, start=path)
        print("{:<15} {:<20}".format(str(Converter(size)), relative_path))
    print("{:<15} {:<20}".format(str(Converter(total)), "./"))
    return 0


if __name__ == "__main__":
    path = os.getcwd()
    if len(sys.argv) > 1:
        path = sys.argv[1]
    print("Starting directory size calculation for %s" % path)

    with ExecutionTimer():
        sys.exit(main(path))
