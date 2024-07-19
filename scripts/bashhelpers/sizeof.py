#!/usr/bin/env python3

# sizeof.py - additianl functionality to `sizeof` bash alias

import os
import subprocess
import argparse

from size import Converter
from ExecutionTimer import ExecutionTimer


def parse_args():
    parser = argparse.ArgumentParser(
        description="Additianl functionality to `sizeof` bash alias",
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
        "-a", "--all", action="store_true", default=False, help="Show file sizes"
    )
    parser.add_argument(
        "-mount",
        action="store_true",
        help="Skip directories on seperate mount points",
        default=False,
    )
    args = parser.parse_args()
    return args


def sizeof(path):
    cmd = "du -b" if not args.all else "du -ab"
    if args.mount:
        cmd += "x"
    output = subprocess.run(
        f"{cmd} {path} | sort -h | tail -{int(args.lines)}",
        shell=True,
        capture_output=True,
        text=True,
    )
    stdout = output.stdout.strip()
    stderr = output.stderr.strip()
    if "denied" not in stderr:
        print(stderr)
    for item in stdout.split("\n"):
        size, directory = item.split("\t")
        print(f"{str(Converter(int(size))).ljust(12)}{directory}")
    return output.stdout if args.all else None


def all_direcorty_sizes(self, path):
    total = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total += os.path.getsize(fp)
    return total


def all_file_sizes(self, path):
    total = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total += os.path.getsize(fp)
    return total


# Example usage
if __name__ == "__main__":
    args = parse_args()
    with ExecutionTimer():
        sizeof(args.path)
