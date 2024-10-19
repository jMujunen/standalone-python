#!/usr/bin/env python3
"""Organize a directory by mimetype.

Additionally, creates an organized tree for any images or videos which get
sorted by capture date and moved to its respective folder"""

import argparse
import os
import re
import shutil
import sys
from pathlib import Path

from Color import cprint
from fsutils import FILE_TYPES, IGNORED_DIRS, File
from fsutils.DirNode import Dir, obj
from ThreadPoolHelper import Pool

MAX_DUPLICATES = 2


DATE_REGEX = re.compile(r"\d{1,4}-(\d{4}).?(\d{2}).?(\d{2}).(\d{2}).?(\d{2}).?(\d{2})")


def cleanup(top) -> None:
    """Remove empty directories recursively."""
    for root, dirs, files in os.walk(top):
        for d in dirs:
            cleanup(os.path.join(root, d))
        if not dirs and not files:
            os.rmdir(root)


def sort_spec_formatter(spec: str) -> str:
    match spec:
        case "year":
            return "%Y"
        case "month":
            return "%Y/%h"
        case "day":
            return "%Y/%h/%d"
        case _:
            raise ValueError(f"Invalid sort spec: {spec}")


def categorize_other(y: File, x: str) -> str:
    """Move files that are not categorized to the other directory based of mimetype.

    Paramaters:
    -----------
        - item (File): The file object.
        - target_root (Dir): The target root directory
    """
    prefix = os.path.join(x, "Other")
    for k, v in FILE_TYPES.items():
        if y.suffix.lower() in v:
            prefix = os.path.join(prefix, k)
    return prefix


def get_prefix(item: File, target: str, sort_spec: str) -> str | None:
    """Categorize a file into the appropriate destination folder based on its type and creation date.

    Parameters
    ----------
        - item (File): The file object.
        - target (str): The target directory path.
        - sort_spec (str): The sorting specification, e.g., 'year', 'month', 'day'
    """
    if item.suffix.lower() in FILE_TYPES["trash"]:
        os.remove(item.path)
        cprint.info(f"Removed {item.name}")
        return None
    for part in item.path.split(os.sep):
        if part in IGNORED_DIRS:
            return None

    match item.__class__.__name__:
        case "Img":
            return (
                os.path.join(target, "Photos", item.capture_date.strftime(sort_spec))  # type: ignore
                if item.suffix.lower() != ".nef"
                else os.path.join(
                    target,
                    "Photos",
                    "RAW",
                    item.capture_date.strftime(sort_spec),  # type: ignore
                )
            )
        case "Video":
            return os.path.join(
                target,
                "Videos",
                item.capture_date.strftime(sort_spec),  # type: ignore
            )
        case "Dir":
            return os.remove(item.path) if not os.listdir(item.path) else None
        case _:
            return categorize_other(item, target)


def determine_originals(file_paths: list[str], num_keep: int) -> list[str]:
    """Given a list of file paths and the number of duplicates to keep,
    return a list of file paths that should be kept.

    Parameters
    -----------
        - `file_paths (list[str])`: A list of file paths.
        - `num_keep (int)`: The number of duplicates to keep
    """
    oldest_to_newest = sorted(file_paths, key=lambda x: os.path.getmtime(x), reverse=False)
    keep = []
    remove = []
    for i, path in enumerate(oldest_to_newest):
        if i < num_keep:
            keep.append(path)
        else:
            remove.append(path)
    return remove


def process_item(
    item: File, target_root: Dir, index: dict[str, list[str]], sort_spec: str, dry_run=False
) -> str | None:
    """Process a single item (file or directory) and move it to the appropriate destination folder.

    Paramaters:
    -------------
        - item (File): The media file to be sorted.
        - target_root (Dir): The root directory where all files will be moved.
        - index(int): The current index of the item in the list of items.
        - sort_spec(str): The sorting specification, either "day", "month" or "year".
    """
    dest_folder = get_prefix(item=item, target=target_root.path, sort_spec=sort_spec)
    if dest_folder is None:
        return None
    os.makedirs(dest_folder, exist_ok=True)
    dest_path = os.path.join(dest_folder, item.name)

    # Check for duplicates in the same directory, keeping MAX_DUPLICATES copies.
    count = 0
    existing_files = index.get(item.sha256(), [])
    while os.path.exists(dest_path):
        if len(existing_files) < MAX_DUPLICATES:
            print(dest_path)
            # Rename the file while under MAX_DUPLICATES
            count += 1
            path, name = os.path.split(dest_path)
            dest_path = os.path.join(path, f"{count}-{item.name}")
        elif len(existing_files) > MAX_DUPLICATES:
            # Remove newest items while MAX_DUPLICATES is exceeded.
            existing_files.append(item.path)
            overflow = sorted(existing_files, key=lambda x: os.path.getmtime(x))
            if dry_run:
                cprint(f"[REMOVE] - {'\n'.join(overflow[MAX_DUPLICATES:])}")
                cprint(f"[KEEP] - {'\n'.join(overflow[:MAX_DUPLICATES])}")
                return None
            for file in overflow[MAX_DUPLICATES:]:
                os.remove(file)
    try:
        shutil.move(item.path, dest_path, copy_function=shutil.copy2)
    except (PermissionError, FileExistsError, FileNotFoundError) as e:
        cprint.error(f"{e}: {e.filename} {e.filename2}")
        raise e from e
    except Exception as e:
        cprint.error(f"Unidentified Error: {e!r}: {item.path} {dest_path}")
        return dest_path


def filter_files(root: Dir, filter_spec: str) -> list[File]:
    """Filter files based on a given specification."""
    filter_spec = filter_spec.capitalize()
    module = sys.modules[__name__]
    FileClass = getattr(module, filter_spec)
    return [item for item in root if isinstance(item, FileClass)]


def main(root: str, destination: str, spec: str, refresh=False, dry_run=False) -> None:
    """Sort files based on media type and date.

    Paramaters:
    ----------
        - `root (str)`: The directory to start sorting from.
        - `destination (str)`: The directory to move sorted files into.
        - `spec (str)`: The file extension to sort by.
        - `refresh (bool)`: Whether or not to refresh the database.
        - `dry_run (bool)`: Whether or not to perform a dry run
    """
    path = Dir(root)
    dest = Dir(destination)

    index = dest.serialize(replace=refresh)
    # If root and destination are the same, do not recurse into subdirectories
    file_objs = [obj(file) for file in path.content] if root == dest else path.file_objects
    sort_spec = sort_spec_formatter(spec)
    pool = Pool()
    list(
        pool.execute(
            process_item,
            file_objs,
            progress_bar=True,
            dry_run=dry_run,
            index=index,
            target_root=dest,
            sort_spec=sort_spec,
        )
    )
    cleanup(root)
    try:
        os.rmdir(root)
    except OSError as e:
        cprint.error(f"OSError while removing dir: {e.strerror}: {e.filename}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Take a directory tree and sort the contents by media type and date",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "ROOT",
        help="The top level directory to start sorting from",
        nargs="?",
        type=str,
        default="./",
    )
    parser.add_argument(
        "DEST",
        help="Destination folder for sorted files",
        type=str,
        nargs="?",
        default="./sorted",
    )
    parser.add_argument(
        "--spec",
        help="Spec file to use for sorting",
        choices=["year", "month", "day"],
        default="year",
    )
    parser.add_argument(
        "-f",
        "--filter",
        help="Only sort this type of file",
        choices=["img", "video", "file"],
    )

    parser.add_argument(
        "--refresh",
        help="Refresh database index before starting",
        action="store_true",
        default=False,
        required=False,
    )
    parser.add_argument(
        "--dry-run",
        help="Print actions instead of performing them",
        action="store_true",
        default=False,
        required=False,
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if not os.path.exists(args.DEST):
        os.makedirs(args.DEST, exist_ok=True)
    main(args.ROOT, args.DEST, args.spec, args.refresh, args.dry_run)
