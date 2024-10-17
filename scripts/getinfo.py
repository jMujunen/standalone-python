#!/usr/bin/env python3
"""Prints the total count of each file type in a given directory."""

import argparse
import os
from collections import defaultdict

from ExecutionTimer import ExecutionTimer
from fsutils import Dir, File
from fsutils.mimecfg import FILE_TYPES

IGNORED = FILE_TYPES.get("ignored", [])


def process_file(file: File, no_ignore=False) -> str | None:
    if not all((filesuffix not in IGNORED, no_ignore)):
        return filesuffix[1:]  # remove the dot from the extension
    return None


def count_file_types(directory: str, no_ignore=False) -> dict:
    """Count the number of files in each type within a given directory.

    Parameters
    ------------
        - `directory (str)` : The path to the directory whose file types are being counted.
        - `no_ignore (bool)` : A flag indicating whether or not to ignore certain file types. Default is False.

    """
    file_types = defaultdict(int)

    files = []
    for item in Dir(directory).file_objects:
        if not all((itemsuffix not in IGNORED, no_ignore)):
            files.append(item)
    for item in files:
        file_types[itemsuffix[1:]] += 1  # remove the dot from the extension
    return dict(sorted(file_types.items(), key=lambda item: item[1]))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", nargs="?", default=os.getcwd())
    parser.add_argument(
        "--no-ignore",
        action="store_true",
        help="Don't ignore files based on the mimecfg",
        default=False,
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    with ExecutionTimer():
        counts = count_file_types(args.directory, args.no_ignore)
        for file_type, count in counts.items():
            print(f"{file_type:<20} {count:>10}")
