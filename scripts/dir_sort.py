#!/usr/bin/env python3

import argparse
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

from Color import cprint, fg, style
from ExecutionTimer import ExecutionTimer
from fsutils import Dir, File, Img, Video
from ProgressBar import ProgressBar


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Take a directory tree and sort the contents by media type and date"
    )
    parser.add_argument("ROOT", help="The top level directory to start sorting from")
    parser.add_argument(
        "-m",
        "--month",
        help="Sort into month directories",
        action="store_true",
        default=True,
        required=False,
    )
    parser.add_argument(
        "-y",
        "--year",
        help="Sort into year directories",
        action="store_true",
        default=False,
        required=False,
    )
    args = parser.parse_args()
    return args


def process_item(item):
    pass


def main(top: str, month: bool, year: bool) -> int:
    with ThreadPoolExecutor() as executor:
        futures = []


if __name__ == "__main__":
    args = parse_args()
    with ExecutionTimer():
        exit(main(args.ROOT, args.month, args.year))
