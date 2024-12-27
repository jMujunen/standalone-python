#!/usr/bin/env python3

import datetime
from collections.abc import Generator
import itertools
from typing import Any
import os
from sys import exit
from size import Size
import argparse
from Color import cprint, fg
from fsutils.dir import Dir, obj
from ThreadPoolHelper import Pool


def gen_stat(lst) -> Generator[zip[Any]]:
    """Given a list of file paths, return a generator tuples of the stat results for each pair
    for each pair of files in the list.
    """
    for i in itertools.combinations(lst, 2):
        pair = obj(i[0]), obj(i[1])
        yield zip(*(p.stat()[-3:] for p in pair), strict=False)


def determine_originals(file_paths: list[str], num_keep: int) -> set[str]:
    """Given a list of file paths and the number of duplicates to keep,
    return a list of file paths that should be kept.

    Parameters
    -----------
        - `file_paths (list[str])`: A list of file paths.
        - `num_keep (int)`: The number of duplicates to keep
    """
    oldest_to_newest = sorted(file_paths, key=os.path.getmtime, reverse=False)
    keep = set()
    remove = set()
    for i, path in enumerate(oldest_to_newest):
        if i < num_keep:
            keep.add(path)
        else:
            for st_result in gen_stat(oldest_to_newest):
                for st in st_result:
                    if st[0] != st[1] and st[0] < st[1]:
                        break
                remove.add(path)
    return remove, keep


def remove_file(file_path, dry_run=False, debug=False) -> int:
    """Calculate size and then remove file."""
    size = os.path.getsize(file_path)
    if not dry_run:
        os.remove(file_path)
    elif dry_run and not debug:
        print(f"Would have removed {file_path}")
    return size


def main(db: dict[str, list[str]], num_keep: int, dry_run=False, debug=False) -> int:
    """Remove newest files for duplicates found in <PATH>."""
    pool = Pool()
    size_of_removed = 0
    num_removed = 0
    result = pool.execute(determine_originals, db.values(), progress_bar=False, num_keep=num_keep)
    print("\nCalculating...")
    for duplicate_items in result:
        remove, _ = duplicate_items
        if debug and remove:
            cprint("Remove:", fg.red)
            for item in remove:
                cprint(f"{item:<60}{datetime.datetime.fromtimestamp(os.path.getmtime(item))}")

            cprint("Keep:", fg.green)
            for item in _:
                cprint(f"{item:<60}{datetime.datetime.fromtimestamp(os.path.getmtime(item))}")
            print("-" * 80)
        if remove:
            size_of_removed += sum(
                pool.execute(remove_file, remove, dry_run=dry_run, debug=debug, progress_bar=False)
            )
            num_removed += len(remove)

    print(f"\nSpace saved: {Size(size_of_removed)!s} by removing {num_removed} files")
    return 0


def parse_args() -> argparse.Namespace:
    """Parse arguments."""
    parser = argparse.ArgumentParser("Remove newest files for duplicates found in <PATH>")
    parser.add_argument("path", help="Path to start search from")
    parser.add_argument("-n", "--num", default=1, type=int, help="Number of duplicates to keep")
    parser.add_argument("--dry-run", action="store_true", required=False, default=False)
    parser.add_argument("--refresh-db", action="store_true", required=False, default=False)
    parser.add_argument("--debug", action="store_true", required=False, default=False)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    dir_object = Dir(args.path)
    if not dir_object.exists():
        print("Path does not exist.")
        exit(1)
    db = dir_object.serialize() if args.refresh_db else dir_object.load_database()
    exit(main(db=db, num_keep=args.num, dry_run=args.dry_run, debug=args.debug))
