#!/usr/bin/env python3

# remove_corrupt_media.py - Finds and removes corrupt images and videos.

import os
import argparse

from ExecutionTimer import ExecutionTimer
from ProgressBar import ProgressBar
from MetaData import *
from Color import *


def parse_arguments():
    parser = argparse.ArgumentParser(description="Finds and removes corrupt images and videos")
    parser.add_argument("path", help="Path to the directory")
    return parser.parse_args()


def main(path):
    with ExecutionTimer():
        corrupted_files = []

        directory = Dir(path)
        jobs = len(directory) + 1

        cprint(f"Found {jobs - 1} files", fg.green, style.bold)
        progress = ProgressBar(jobs)
        for item in directory:
            progress.increment()
            if item.is_file and item.is_image or item.is_video:
                if item.is_corrupt:
                    cprint(f"{item.path} is corrupt. Removing...", fg.red, style.bold)
                    corrupted_files.append(item.path)
        print("")

        with open("corrupt_files.txt", "w") as f:
            f.write("\n".join(corrupted_files))

        print("\n".join(corrupted_files))

    if input("Are you sure you want to remove these files? [y/N]: ") in ["y", "Y"]:
        os.system("clear")
        remove_progress = ProgressBar(len(corrupted_files))
        for f in corrupted_files:
            remove_progress.increment()
            try:
                os.remove(f)
            except KeyboardInterrupt:
                break
            except Exception as e:
                cprint(f"\n{e}", fg.red, style.bold)
                continue


if __name__ == "__main__":
    args = parse_arguments()
    main(args.path)
