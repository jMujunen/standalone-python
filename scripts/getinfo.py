#!/usr/bin/env python3
"""Prints the total count of each file type in a given directory."""

import argparse
import os
from collections import defaultdict
from pathlib import Path

from ExecutionTimer import ExecutionTimer
from fsutils.compiled._DirNode import Dir, File
from fsutils.mimecfg import FILE_TYPES

IGNORED = FILE_TYPES.get("ignored", [])


def count_file_types(directory: str) -> dict:
    """Count the number of files in each type within a given directory.

    Parameters
    ------------
        - `directory (str)` : The path to the directory whose file types are being counted.
        - `no_ignore (bool)` : A flag indicating whether or not to ignore certain file types. Default is False.

    """
    file_types = defaultdict(int)
    filepaths = Dir(directory).ls()
    exts = [
        path.split(".")[-1]
        for path in filepaths
        if not any(ignored in Path(path).parts for ignored in IGNORED)
    ]
    for ext in exts:
        file_types[ext] += 1
    return dict(sorted(file_types.items(), key=lambda item: item[1]))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", nargs="?", default=os.getcwd())
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    with ExecutionTimer():
        counts = count_file_types(args.directory)
        for file_type, count in counts.items():
            print(f"{file_type:<20} {count:>10}")
