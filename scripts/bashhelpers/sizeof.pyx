#!/usr/bin/env python3
"""Adds functionality to `sizeof` (du -s) bash alias."""

import argparse
import subprocess
cimport cython
import os
import fnmatch
import sys
from ExecutionTimer import ExecutionTimer
from size import Size



cdef int main(str path, int lines, list[str] exclude, bint include_files, bint one_filesystem):
    """`du` wrapper.

    Args:
    -----
        path (str): Path to directory.
        lines (int): Number of lines to print.
        exclude (list[str]): List of patterns to exclude.
        include_files (bool, optional): Write counts for all files, not just directories
        one_filesystem (bool, optional): Skip directories on separate mount points. Defaults to False.

    Returns:
    -------
        str | None: stdout if filesizes is True else None
    """
    # Build the command to be executed based on the given arguments.
    cdef str size, dir
    cdef list[str] cmd
    cdef list[list[str]] result
    cdef int num_errors

    cmd = ["du", "-b"] if not include_files else ["du",  "-ab"]
    if one_filesystem:
        cmd.append("-x")
    for pattern in exclude:
        cmd.append(f"--exclude={pattern}")

    # Execute the command using capturing both stdout and stderr.
    du = subprocess.run([*cmd, path], capture_output=True)

    if du.stderr:
        num_errors = len(du.stderr.decode().splitlines())
        print(f"There were {num_errors} errors.")

    result = sorted([x.split('\t') for x in du.stdout.decode().splitlines()], key=lambda x: int(x[0]))[-lines:]


    for size, dir  in result:
        print(f"{Size(int(size))!s:<12}{dir}")
    return 0

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
    parser.add_argument("-l", "--lines", type=int, default=1, help="Show top N directories")
    parser.add_argument(
        "-a",
        "--all",
        action="store_true",
        help="Show file sizes",
    )
    parser.add_argument(
        "-1",
        "--one-filesystem",
        action="store_true",
        help="Skip directories on separate mount points",
    )

    parser.add_argument(
        "-X",
        "--exclude",
        action="extend",
        nargs='+',
        default=[],
        help="Ignore directories or files glob pattern",
    )
    return parser.parse_args()

# Example usage
if __name__ == "__main__":
    import os, sys
    args = parse_args()
    if not os.path.exists(args.path):
        print(f"Error: {args.path} does not exist.")
        sys.exit(1)
    with ExecutionTimer():
        try:
            sys.exit(main(args.path, args.lines, args.exclude, args.all, args.one_filesystem))
        except KeyboardInterrupt:
            sys.exit(1)

