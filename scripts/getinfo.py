#!/usr/bin/env python3
"""Prints the total count of each file type in a given directory"""

import argparse
import os
from collections import defaultdict

from fsutils import Dir
from fsutils.mimecfg import FILE_TYPES
from ProgressBar import ProgressBar

IGNORED = FILE_TYPES.get("ignored", [])


def count_file_types(directory: str, ignore=False) -> dict:
    # TODO : Implement ignored flag
    file_types = defaultdict(int)
    files = [i for i in Dir(directory).file_objects if i.extension not in IGNORED]
    with ProgressBar(len(files)) as progress:
        for item in files:
            progress.increment()
            file_types[item.extension[1:]] += 1  # remove the dot from the extension
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
