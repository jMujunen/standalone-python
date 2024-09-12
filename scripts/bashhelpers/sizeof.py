#!/usr/bin/env python3
"""Adds functionality to `sizeof` (du -s) bash alias."""

import argparse
import os
import subprocess

from ExecutionTimer import ExecutionTimer
from size import Size


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Additional functionality to `sizeof` bash alias",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to directory. Defaults to current directory.",
    )
    parser.add_argument("-l", "--lines", type=int, default=1)
    parser.add_argument(
        "-a",
        "--all",
        action="store_true",
        default=False,
        help="Show file sizes",
    )
    parser.add_argument(
        "-mount",
        action="store_true",
        help="Skip directories on seperate mount points",
        default=False,
    )
    return parser.parse_args()


def sizeof(path: str, lines: int, filesizes: bool) -> str | None:
    cmd = "du -b" if not args.all else "du -ab"
    if args.mount:
        cmd += "x"
    output = subprocess.run(
        f"{cmd} {path} | sort -h | tail -{int(lines)}",
        shell=True,
        capture_output=True,
        text=True,
        check=False,
    )
    stdout = output.stdout.strip()
    stderr = output.stderr.strip()
    if "denied" not in stderr:
        print(stderr)
    for item in stdout.split("\n"):
        size, directory = item.split("\t")
        print(f"{str(Size(int(size))).ljust(12)}{directory}")
    return output.stdout if filesizes else None


# Example usage
if __name__ == "__main__":
    args = parse_args()
    with ExecutionTimer():
        sizeof(args.path, args.lines, args.all)
