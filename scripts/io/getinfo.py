#!/usr/bin/env python3
"""Prints the total count of each file type in a given directory."""

import argparse
import os
from collections import defaultdict
from pathlib import Path

from ExecutionTimer import ExecutionTimer
from fsutils.dir import Dir


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description=__doc__,
        exit_on_error=False,
    )
    parser.add_argument("directory", nargs="?", default=os.getcwd())
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    total = 0
    with ExecutionTimer():
        counts = Dir(args.directory).describe()
