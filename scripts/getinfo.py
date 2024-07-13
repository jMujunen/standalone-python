#!/usr/bin/env python3
"""Prints the total count of each file type in a given directory"""

import os
import sys
from collections import defaultdict
from ExecutionTimer import ExecutionTimer
from fsutils.mimecfg import FILE_TYPES

IGNORED = FILE_TYPES.get("ignored")

DIRECTORY = os.getcwd()


def count_file_types(directory: str) -> dict:
    file_types = defaultdict(int)
    for root, dirs, files in os.walk(directory):
        for file in files:
            _, ext = os.path.splitext(file)
            if ext and ext not in IGNORED:
                file_types[ext[1:]] += 1  # remove the dot from the extension
    return dict(sorted(file_types.items(), key=lambda item: item[1]))


if __name__ == "__main__":
    if len(sys.argv) > 1:
        DIRECTORY = "".join(sys.argv[1:])
    with ExecutionTimer():
        counts = count_file_types(DIRECTORY)
        for file_type, count in counts.items():
            print("{:<20} {:>10}".format(file_type, count))
