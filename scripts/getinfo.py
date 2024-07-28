#!/usr/bin/env python3
"""Prints the total count of each file type in a given directory"""

import argparse
import os
from collections import defaultdict

from ProgressBar import ProgressBar

from fsutils import Dir
from fsutils.mimecfg import FILE_TYPES

IGNORED = FILE_TYPES.get("ignored", [])


def count_file_types(directory: str, ignore=False) -> dict:
    """
    Counts the total number of each file type in a given directory and its subdirectories.

    Args:
        directory (str): The path to the directory to be counted.
        ignore (bool): If True, ignores specific file types as specified in FILE_TYPES configuration.

    Returns:
        dict: A dictionary where keys are file extensions (without a leading dot) and values are their counts.

    This function uses the fsutils library to traverse through the directory tree. It keeps track of each file type's count,
    optionally ignoring certain types based on configuration settings from FILE_TYPES. The results are returned as a sorted dictionary.
    """
    file_types = defaultdict(int)
    path = Dir(directory)
    with ProgressBar(len(path)) as progress:
        for item in path:
            progress.increment()
            ext = item.extension
            if not ignore and ext and ext not in IGNORED:
                file_types[ext[1:]] += 1  # remove the dot from the extension
            elif ext:
                file_types[ext[1:]] += 1  # remove the dot from the extension
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
    counts = count_file_types(args.directory, args.no_ignore)
    for file_type, count in counts.items():
        print(f"{file_type:<20} {count:>10}")
