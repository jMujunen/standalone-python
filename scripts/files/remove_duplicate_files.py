#!/usr/bin/env python3
"""remove_duplicate_media.py - Finds and removes duplicate files and videos."""

import argparse
import datetime
import os
from collections import OrderedDict

from Color import cprint, fg, style
from ExecutionTimer import ExecutionTimer
from fsutils import Dir, File, Img
from ThreadPoolHelper import Pool

IGNORED_DIRS = [".Trash-1000"]


def process_file(file: File) -> tuple[int, str] | None:
    """Function for concurrent processing. This is called from the ThreadPool."""
    if (ignored in file.path for ignored in IGNORED_DIRS) or not file.exists:
        return
    return (hash(file), file.path)


def generate_hash_map(path: str, images=False, videos=False) -> OrderedDict:
    """Find duplicate files based on their hash representation"""

    def filter(images: bool, videos: bool):
        match (images, videos):
            case (True, False):
                yield from Dir(path).images
            case (False, True):
                yield from Dir(path).videos
            case _:
                yield from Dir(path).file_objects

    # Create a generator that yields the specified (optional) types of files in the directory
    files = filter(images, videos)
    hashes = OrderedDict()
    # Create a thread pool for concurrent processing
    pool = Pool()
    for result in pool.execute(process_file, list(files), progress_bar=True):
        try:
            if result is not None:
                # Unpack the hash and path from the result
                file_hash, file_path = result
                try:
                    # Try to append the current file path to the list of paths for this hash.
                    hashes[file_hash].append(file_path)
                except (IndexError, KeyError):
                    # Create key if key and set the value if key does not exist yet.
                    hashes[file_hash] = [file_path]
        except TypeError:
            pass  # Ignore exceptions from trying to read bytes object as string
    return hashes


def remove_group(duplicate_group: list[str]) -> bool:
    """Process the hashes object returned from find_duplicates()

    If not in dry run mode and the removal is confirmed, it deletes the extra files
    starting from the third occurrence
    """
    sorted_files = sorted(duplicate_group, key=lambda x: os.path.getmtime(x[1][0]), reverse=False)
    for i, _file in enumerate(sorted_files):
        if i <= 1:  # Skip the first two files
            continue
        try:
            os.remove(_file)
            cprint(f"{_file} removed", fg.green, style.bold)
        except FileNotFoundError:
            continue
        except Exception as e:
            cprint(f"Error removing {_file}: {e!r}\n", fg.red, style.bold)
    print()  # Newline after removing group
    return True


def remove_with_confirmation(duplicate_group: list[str], images=False):
    sorted_files = sorted(duplicate_group, key=lambda x: os.path.getmtime(x[1][0]), reverse=False)
    for file in sorted_files:
        if images:
            Img.show(file)
        else:
            print(file)
    reply = input(
        "\n\033[1mAre you sure you want to remove all but 2 of these files? (y/N)\033[0m: "
    ).lower()
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
    return parser.parse_args()


def main(args: argparse.Namespace) -> None:
    with ExecutionTimer():
        _counter = 0
        # Create a dict mapping of hashed values to their associated files
        hashes = generate_hash_map(args.path, images=args.images, videos=args.videos)
        duplicate_files = [v for v in hashes.values() if len(v) >= 3]
        cprint(f"\n{len(duplicate_files)} duplicates found:", fg.cyan, style.bold)
        # Use a threadpool to remove duplicates if no_confirm  is set (for speed)
        if not args.dry_run and args.no_confirm:
            pool = Pool()
            for result in pool.execute(remove_group, duplicate_files):
                if result:
                    _counter += 1
        elif not args.dry_run and not args.no_confirm:
            for group in duplicate_files:
                remove_with_confirmation(group, images=args.images)
        else:
            for group in duplicate_files:
                sorted_group = sorted(group, key=lambda x: os.path.getmtime(x), reverse=False)
                for i, file in enumerate(sorted_group):
                    os.path.split(file)[-1]
                    if i <= 1:
                        cprint(
                            f"[DRY-RUN] Keeping {file:<100} {datetime.datetime.fromtimestamp(os.path.getmtime(file)).strftime(
                "%Y-%m-%d %H:%M:%S")}",
                            fg.green,
                        )
                    else:
                        cprint(
                            f"[DRY-RUN] removing {file:<100}  {datetime.datetime.fromtimestamp(os.path.getmtime(file)).strftime(
                "%Y-%m-%d %H:%M:%S")}",
                            fg.orange,
                        )
                print("-" * 50)

    return None


if __name__ == "__main__":
    args = parse_args()
    try:
        main(args)
    except KeyboardInterrupt:
        exit(0)
