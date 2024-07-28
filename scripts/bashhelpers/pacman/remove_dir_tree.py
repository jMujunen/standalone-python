#!/usr/bin/env python3

# remove_dir_tree.py - Places all files in a directory tree into a single location
# and removes the original directory tree.

import argparse
import os
import shutil
import subprocess

from ExecutionTimer import ExecutionTimer
from ProgressBar import ProgressBar


def parse_args():
    parser = argparse.ArgumentParser(
        description="Moves all files in a directory tree into a single location and removes the original directory tree.",
        usage="remove_dir_tree.py [OPTIONS] INPUT_DIRECTORY OUTPUT_DIRECTORY",
    )
    parser.add_argument(
        "INPUT_DIRECTORY",
        help="directory to remove",
        type=str,
    )
    parser.add_argument(
        "OUTPUT_DIRECTORY",
        help="output directory",
        type=str,
        default=".",
    )
    parser.add_argument(
        "v",
        "verbose",
        help="increase output verbosity",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "f",
        "force",
        help="force remove",
        action="store_true",
        default=False,
    )
    parser.add_argument("-d", "--dry", help="dry run", action="store_true", default=False)
    return parser.parse_args()


def get_number_of_files(directory):
    number_of_files = subprocess.run(
        f"find {directory} -type f | wc -l", shell=True, capture_output=True, text=True, check=False
    ).stdout.strip()
    return number_of_files


def main():
    args = parse_args()
    number_of_files = get_number_of_files(args.INPUT_DIRECTORY)

    with ProgressBar(int(number_of_files)) as pb:
        files = subprocess.run(
            f"find {args.INPUT_DIRECTORY} -type f",
            shell=True,
            capture_output=True,
            text=True,
            check=False,
        ).stdout.strip()
        files = files.split("\n")

        for file in files:
            pb.increment()
            try:
                output_path = os.path.join(args.OUTPUT_DIRECTORY, os.path.basename(file))
                if args.dry:
                    print(f"{file} -> {output_path}.")
                else:
                    shutil.move(file, output_path)
                    if args.verbose:
                        print(f"{file} -> {output_path}")

                # pb.increment()
            except Exception as e:
                print(e)


if __name__ == "__main__":
    with ExecutionTimer():
        main()
