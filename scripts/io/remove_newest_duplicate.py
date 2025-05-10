#!/usr/bin/env python3

import datetime
from collections.abc import Generator
from itertools import combinations
from typing import Any
import os
from sys import exit
from size import Size
import argparse
from Color import cprint, fg
from fsutils.dir import Dir, obj
from ThreadPoolHelper import Pool
from decorators import exectimer


def process_files(
    file_paths: list[str], num_keep: int = 2, dry_run: bool = False
) -> tuple[int, int]:
    """Given a list of file paths and the number of duplicates to keep,
    return a list of file paths that should be kept.

    Parameters
    -----------
        - `file_paths (list[str])`: A list of file paths.
        - `num_keep (int)`: The number of duplicates to keep
    """

    def sort_key(filepath: str) -> tuple[float, float, float]:
        st = os.stat(filepath)
        return (st.st_ctime, st.st_mtime, st.st_atime)

    oldest_to_newest = sorted(file_paths, key=sort_key, reverse=False)
    size = 0
    count = 0
    for i, path in enumerate(oldest_to_newest):
        if i < num_keep:
            # keep.add(path)
            continue
        # remove.append(path)
        size += remove_file(path, dry_run=dry_run)
        count += 1
    return size, count


def remove_file(file_path, dry_run=False, debug=False) -> int:
    """Calculate size and then remove file."""
    size = os.path.getsize(file_path)
    if not dry_run:
        os.remove(file_path)
    elif dry_run and not debug:
        print(f"Would have removed {file_path}")
    return size


def main(db: dict[str, set[str]], num_keep: int, dry_run=False, debug=False) -> int:
    """Remove newest files for duplicates found in <PATH>."""
    pool = Pool()
    size_of_removed = 0
    num_removed = 0
    print("\nCalculating...")
    for duplicate_items in pool.execute(
        process_files,
        db.values(),
        progress_bar=True,
        num_keep=num_keep,
        dry_run=dry_run,
    ):
        size, count = duplicate_items
        size_of_removed += size
        num_removed += count
        # if debug and remove:
        #     cprint("Remove:", fg.red)
        #     for item in remove:
        #         cprint(f"{item:<120}{datetime.datetime.fromtimestamp(os.path.getmtime(item))}")

        #     cprint("Keep:", fg.green)
        #     for item in _:
        #         cprint(f"{item:<120}{datetime.datetime.fromtimestamp(os.path.getmtime(item))}")
        #     print("-" * 80)
        # elif remove:
        #     size_of_removed = sum()
        #     num_removed += len(remove)

    print(f"\nSpace saved: {Size(size_of_removed)!s} by removing {num_removed} files")
    return 0


def parse_args() -> argparse.Namespace:
    """Parse arguments."""
    # parser = argparse.ArgumentParser()
    parser = argparse.ArgumentParser(
        description="Remove newest files for duplicates found in <PATH>"
    )
    parser.add_argument("path", help="Path to start search from")
    parser.add_argument(
        "-n", "--num", default=1, type=int, help="Number of duplicates to keep"
    )
    parser.add_argument("--dry-run", action="store_true", required=False, default=False)
    parser.add_argument(
        "--refresh-db", action="store_true", required=False, default=False
    )
    parser.add_argument("--debug", action="store_true", required=False, default=False)
    return parser.parse_args()


if __name__ == "__main__":
    # path = Dir("/mnt/hddred/rsync/Arch/joona/python")
    # db = path.db
    # exit(main(db=db, num_keep=2, dry_run=True, debug=False))
    args = parse_args()
    dir_object = Dir(args.path)
    if not dir_object.exists():
        print("Path does not exist.")
        exit(1)
    db = dir_object.serialize() if args.refresh_db else dir_object.load_database()
    exit(main(db=db, num_keep=args.num, dry_run=args.dry_run, debug=args.debug))
