#!/usr/bin/env python3
"""Prints the total count of each file type in a given directory"""

import argparse
import os
import sys
from collections import defaultdict

from ExecutionTimer import ExecutionTimer
from fsutils import Dir
from fsutils.mimecfg import FILE_TYPES
from ProgressBar import ProgressBar

IGNORED = FILE_TYPES.get("ignored", [])

DIRECTORY = os.getcwd()


def count_file_types(directory: str, ignore=False) -> dict:
    file_types = defaultdict(int)
    path = Dir(directory)
    # progress = ProgressBar(len(path))
    with ProgressBar(len(path)) as progress:
        for item in path:
            progress.increment()
            ext = item.extension
            if not ignore:
                if ext and ext not in IGNORED:
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
    if len(sys.argv) > 1:
        DIRECTORY = "".join(sys.argv[1:])
    with ExecutionTimer():
        counts = count_file_types(DIRECTORY, args.no_ignore)
        for file_type, count in counts.items():
            print(f"{file_type:<20} {count:>10}")
