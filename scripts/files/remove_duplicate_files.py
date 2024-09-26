#!/usr/bin/env python3
"""remove_duplicate_media.py - Finds and removes duplicate files and videos."""

import argparse
import datetime
import os
import sys
from collections import OrderedDict

from Color import cprint, fg, style
from ExecutionTimer import ExecutionTimer
from fsutils import Dir, File, Img
from ThreadPoolHelper import Pool

IGNORED_DIRS = [".Trash-1000"]

MAX_DUPLICATE_FILES = 3


def process_file(file: File) -> tuple[int, str] | None:
    """Concurrent processing. This is called from the ThreadPool instance."""
    if any(ignored in file.path for ignored in IGNORED_DIRS) or not file.exists:
        return None
    return (hash(file), file.path)


def remove_group(duplicate_group: list[str]) -> bool:
    """Process the hashes object returned from find_duplicates().

    If not in dry run mode and the removal is confirmed, it deletes the extra files
    starting from the third occurrence
    """
    sorted_files = sorted(duplicate_group, key=lambda x: os.path.getmtime(x[0]), reverse=False)
    _counter = 0
    for i, _file in enumerate(sorted_files):
        if i <= 1:  # Skip the first two files
            continue
        try:
            os.remove(_file)
            _counter += 1
        except FileNotFoundError:
            continue
        except Exception as e:
            cprint(f"Error removing {_file}: {e!r}\n", fg.red, style.bold)
    return True


def remove_with_confirmation(duplicate_group: list[str], images=False) -> bool:
    """Process the hashes returned from `find_duplicates()`."""
    sorted_files = sorted(duplicate_group, key=lambda x: os.path.getmtime(x[0]), reverse=False)
    for i, file in enumerate(sorted_files):
        if i <= 1:  # Skip the first two files
            print(f"{fg.green}[KEEP]{style.reset}", end=" ")
            if images:
                Img(file).render(title=True)
            else:
                print(file)
            continue
        print(f"{fg.red}{style.bold}[REMOVE]{style.reset}", end=" ")
        if images:
            Img(file).render(title=True)
    reply = input("\n\033[1mAre you sure you want to remove these files? (y/N)\033[0m: ").lower()
    if reply in ["y", "yes"]:
        return remove_group(duplicate_group)
    return False


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Remove duplicate image files from a folder.",
    )
    parser.add_argument("path", help="Path to the directory")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only print the duplicate files that would be removed",
    )
    parser.add_argument("--no-confirm", help="Remove without confirmation", action="store_true")
    parser.add_argument("--images", help="Only process image files", action="store_true")
    parser.add_argument("--videos", help="Only process video files", action="store_true")
    parser.add_argument("--quiet", help="Suppress output", action="store_true")
    parser.add_argument("--refresh", help="Re-index path files before comparing")
    return parser.parse_args()


def main(
    root: str,
    images: bool,
    videos: bool,
    quiet: bool,
    dry_run: bool,
    no_confirm: bool,
    refresh: bool,
) -> None:
    with ExecutionTimer():
        _counter = 0
        root_path = Dir(root)
        # Create a dict mapping of hashed values to their associated files
        hashes = root_path.serialize(replace=True) if refresh else root_path.load_database()

        duplicate_files = [v for v in hashes.values() if len(v) >= MAX_DUPLICATE_FILES]
        cprint(f"\n{len(duplicate_files)} duplicates found:", style.bold)
        # Use a threadpool to remove duplicates if no_confirm  is set (for speed)
        if not dry_run and no_confirm:
            pool = Pool()
            for result in pool.execute(remove_group, duplicate_files, progress_bar=False):
                if result is True:
                    _counter += 1
        # Remove with confirmation
        elif not args.dry_run and not args.no_confirm:
            for group in duplicate_files:
                remove_with_confirmation(group, images=images)
        # Print duplicates without removing them
        else:
            for group in duplicate_files:
                sorted_group = sorted(group, key=lambda x: os.path.getmtime(x), reverse=False)
                for i, file in enumerate(sorted_group):
                    os.path.split(file)[-1]
                    if not args.quiet and i <= 1:
                        _counter += 1
                        cprint(
                            f"[DRY-RUN] Keeping {file:<100} {
                                datetime.datetime.fromtimestamp(os.path.getmtime(file)).strftime(
                                    "%Y-%m-%d %H:%M:%S"
                                )
                            }",
                            fg.green,
                        )
                    elif not args.quiet and i > 1:
                        cprint(
                            f"[DRY-RUN] removing {file:<100}  {
                                datetime.datetime.fromtimestamp(os.path.getmtime(file)).strftime(
                                    "%Y-%m-%d %H:%M:%S"
                                )
                            }",
                            fg.orange,
                        )
                    else:
                        print(file)
                print("-" * 50)
            cprint(f"Found {_counter} duplicates", fg.green)
        print("-" * 50)
        print(f"Removed {style.bold}{_counter}{style.reset} files")


if __name__ == "__main__":
    args = parse_args()
    try:
        main(
            args.path,
            args.images,
            args.videos,
            args.quiet,
            args.dry_run,
            args.no_confirm,
            args.refresh,
        )
    except KeyboardInterrupt:
        sys.exit(0)
