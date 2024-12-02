#!/usr/bin/env python3
"""Adds functionality to `sizeof` (du -s) bash alias."""

import argparse
import subprocess

cimport cython
from ExecutionTimer import ExecutionTimer
from size import Size

SIZE_FORMAT = 12


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
        help="Skip directories on separate mount points",
        default=False,
    )
    return parser.parse_args()


cpdef void main(str path, unsigned short int lines, bint include_files, bint one_filesystem):
    """`du` wrapper.

    Args:
    -----
        path (str): Path to directory.
        lines (int): Number of lines to print.
        include_files (bool, optional): Write counts for all files, not just directories
        one_filesystem (bool, optional): Skip directories on separate mount points. Defaults to False.

    Returns:
    -------
        str | None: stdout if filesizes is True else None
    """
    # Build the command to be executed based on the given arguments.
    cdef str cmd, output, size, directory
    cmd = "du -b" if not include_files else "du -ab"
    if one_filesystem:
        cmd += "x"
    # Execute the command using capturing both stdout and stderr.
    output = subprocess.getoutput(f"{cmd} {path} | sort -h | tail -{int(lines)}")
    for item in output.split("\n"):
        if not 'Permission denied' in item:
            size, directory = item.split("\t")
            print(f"{str(Size(int(size))).ljust(12)}{directory}")


# Example usage
if __name__ == "__main__":
    args = parse_args()

    with ExecutionTimer():
        main(args.path, args.lines, args.all, args.mount)
