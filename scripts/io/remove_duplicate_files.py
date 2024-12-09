#!/usr/bin/env python3
"""remove_duplicate_media.py - Finds and removes duplicate files and videos."""

import argparse
import os
import sys
from collections.abc import Generator

from Color import cprint, fg, style
from ExecutionTimer import ExecutionTimer
from fsutils.dir import Dir
from fsutils.file import File

from ThreadPoolHelper import Pool

IGNORED_DIRS = [".Trash-1000"]

MAX_DUPLICATE_FILES = 2


def process_file(file: File) -> tuple[int, str] | None:
    """Concurrent processing. This is called from the ThreadPool instance."""
    if any(ignored in file.path for ignored in IGNORED_DIRS) or not file.exists:
        return None
    return (hash(file), file.path)


def determine_originals(file_paths: list[str], num_keep: int) -> list[str]:
    """Given a list of file paths and the number of duplicates to keep,
    return a list of file paths that should be kept.

    Parameters
    -----------
        - `file_paths (list[str])`: A list of file paths.
        - `num_keep (int)`: The number of duplicates to keep
    """
    oldest_to_newest = sorted(file_paths, key=os.path.getmtime, reverse=False)
    keep = []
    remove = []
    for i, path in enumerate(oldest_to_newest):
        if i < num_keep:
            keep.append(path)
        else:
            remove.append(path)
    return remove


def remove_group(
    file_paths: list[str], num_keep: int = MAX_DUPLICATE_FILES, dry_run: bool = False
) -> Generator:
    """Remove the oldest duplicates in each group."""
    for file in determine_originals(file_paths, num_keep=num_keep):
        if not dry_run:
            os.remove(file)
        yield file


def main(root: str, dry_run=False, refresh=False, verbose=False) -> None:
    count = 0
    with ExecutionTimer():
        root_dir = Dir(root)
        # Create a dict mapping of hashed values to their associated files
        duplicate_groups = root_dir.duplicates(refresh=refresh)
        num_duplicates = sum([len(group) for group in duplicate_groups]) - len(duplicate_groups)
        cprint.info(f"\n{len(duplicate_groups)} sets,  {num_duplicates} duplicate files:")
        # Use a threadpool to remove duplicates if no_confirm  is set (for speed)
        pool = Pool()
        for result in pool.execute(
            remove_group, duplicate_groups, progress_bar=False, dry_run=dry_run
        ):
            if verbose:
                for file in result:
                    cprint(f"Removed {file}", fg.red)
            count += 1
    cprint.info(f"\n{count} duplicates removed")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Remove duplicate image files from a folder.",
    )
    parser.add_argument("path", help="Path to the directory")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only print the duplicate files that would be removed",
        default=False,
    )

    parser.add_argument(
        "--refresh", help="Re-index path files before comparing", action="store_true", default=False
    )
    parser.add_argument(
        "--verbose", help="Print more information", action="store_true", default=False
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    try:
        main(args.path, args.dry_run, args.refresh, args.verbose)
    except KeyboardInterrupt:
        sys.exit(0)
