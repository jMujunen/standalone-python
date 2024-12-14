#!/usr/bin/env python3
"""Finds and removes corrupt images and videos."""

import argparse
import os
import sys

from Color import cprint, fg, style
from fsutils.dir import Dir, Img, Video
from ThreadPoolHelper import Pool


def process_file(item: Img | Video) -> tuple[bool, str]:
    return item.is_corrupt, item.path


def main(path: str, dry_run: bool) -> None:
    # Create an instance of ThreadPoolHelper's Pool class for parallel execution
    pool = Pool()
    # Combine images and videos in a single list
    files = Dir(path).images + Dir(path).videos
    num_files = len(files)

    cprint(f"Processing {style.bold}{num_files}{style.reset} items", fg.green, style.bold)

    results = pool.execute(process_file, files, progress_bar=True)
    corrupted_files = [path for (corrupt, path) in results if corrupt]
    print("\n".join(corrupted_files))

    if not dry_run and corrupted_files:
        if input("Are you sure you want to remove these files? [y/N]: ") in {"y", "Y"}:
            for f in corrupted_files:
                try:
                    os.remove(f)
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    cprint(f"\n{e!r}", fg.red, style.bold)
                    continue

        print(f"\nDone: {len(corrupted_files)} successfully removed")


def parse_arguments():
    parser = argparse.ArgumentParser(description="Finds and removes corrupt images and videos")
    parser.add_argument("path", help="Path to the directory")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Do not remove files, only show what would be done",
    )
    return parser.parse_args()


if __name__ == "__main__":
    try:
        args = parse_arguments()
        main(args.path, args.dry_run)
    except KeyboardInterrupt:
        sys.exit(127)
