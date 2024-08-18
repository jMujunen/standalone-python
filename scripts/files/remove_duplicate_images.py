#!/usr/bin/env python3
""" "remove_duplicate_media.py - Finds and removes duplicate files and videos."""

import argparse
import os
from collections import OrderedDict

from Color import cprint, fg, style
from ExecutionTimer import ExecutionTimer
from fsutils import Dir, File, Img
from ThreadPoolHelper import Pool

IGNORED_DIRS = [".Trash-1000"]


def process_file(file: File) -> tuple[int, str] | None:
    """Function for concurrent processing. This is called from the ThreadPool."""
    if any(ignored in file.path for ignored in IGNORED_DIRS) or not file.exists:
        return
    return (hash(file), file.path)


def generate_hash_map(path: str, images=False, videos=False) -> tuple[OrderedDict, int]:
    """Find duplicate files based on their hash representation"""
    if images and not videos:
        files = Dir(path).images
    elif videos and not images:
        files = Dir(path).videos
    elif images and videos:
        p = Dir(path)
        files = p.videos
        files.extend(p.images)
    else:
        files = Dir(path).file_objects
    hashes = OrderedDict()
    num_files = len(files)
    num_duplicates = 0
    cprint(f"Found {num_files} files", fg.green, style.bold)
    # Create a thread pool for concurrent processing
    pool = Pool()
    for result in pool.execute(process_file, files, progress_bar=True):
        try:
            if result is not None:
                # Unpack the hash and path from the result
                file_hash, file_path = result
                try:
                    hashes[file_hash].append(file_path)
                    num_duplicates += 1
                except (IndexError, KeyError):
                    hashes[file_hash] = [file_path]
        except TypeError:
            pass  # Ignore exceptions from trying to read bytes object as string
    return hashes, num_duplicates


# def generate_hashes(path: str) -> OrderedDict:
#     """Generate a dictionary of file hashes for all image files under path."""
#     hashes = OrderedDict()
#     # Create a directory object for the given path
#     files = Dir(path).file_objects
#     with Pool() as pool:
#         for result in pool.execute(process_file, files):
#             if result is not None:
#                 # Unpack the hash and path from the result
#                 image_hash, image_path = result
#                 try:
#                     hashes[image_hash].append(image_path)
#                 except (IndexError, KeyError):
#                     hashes[image_hash] = [image_path]
#     return hashes


def remove_group(duplicate_group: list[str]) -> bool:
    """Process the hashes object returned from find_duplicates()

    If not in dry run mode and the removal is confirmed, it deletes the extra files
    starting from the third occurrence
    """
    for i, _file in enumerate(duplicate_group):
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
    for file in duplicate_group:
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
        hashes, num_dupes = generate_hash_map(args.path, images=args.images, videos=args.videos)
        cprint(f"\n{num_dupes} duplicates found:", fg.cyan, style.bold)
        duplicate_files = [v for v in hashes.values() if len(v) >= 3]
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
                for i, file in enumerate(group):
                    basename = os.path.split(file)[-1]
                    if i <= 1:
                        cprint(f"[DRY-RUN] Keeping {file}", fg.green)
                    else:
                        cprint(f"[DRY-RUN] removing {file}", fg.orange)
                print("-" * 50)

    return None


if __name__ == "__main__":
    args = parse_args()
    try:
        main(args)
    except KeyboardInterrupt:
        exit(0)
