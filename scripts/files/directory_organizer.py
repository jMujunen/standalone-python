#!/usr/bin/env python3
"""Organize a directory by mimetype.

Additionally, creates an organized tree for any images or videos which get
sorted by capture date and moved to its respective folder"""

import argparse
import os
import re
import shutil
from datetime import datetime

from Color import cprint, fg, style
from fsutils import FILE_TYPES, File, Img, Video
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


def detect_duplicates(
    src_object: File, dest_filepath: str, index: dict[str, list[str]], dry_run=False
) -> str | None:
    """Detect if a duplicate exists and returns a unique filename."""


def categorize_item(
    item: File, target_root: Dir, index, sort_by="month", dry_run=False
) -> str | None:
    """
    Categorize a file into the appropriate destination folder based on its type and creation date.
    """
    dest_folder = ""
    if isinstance(item, Img):
        prefix = os.path.join(target_root.path, "Photos")
        if item.extension.lower() == ".nef":
            prefix = os.path.join(prefix, "RAW")
    # Set the destination folder to Videos for video files
    elif isinstance(item, Video):
        prefix = os.path.join(target_root.path, "Videos")
    elif isinstance(item, Dir):
        # Remove the directory if it's empty
        if item.is_empty:
            os.rmdir(item.path)
        return None
    else:
        # Set the destination folder to Other for other types of files
        prefix = os.path.join(target_root.path, "Other")
        for k, v in FILE_TYPES.items():
            if os.path.splitext(item.path)[1] in v:
                # prefix = os.path.join(prefix, k)
                prefix = os.path.join(prefix, k)
        dest_path = os.path.join(prefix, item.basename)
        if not os.path.exists(prefix):
            os.makedirs(prefix, exist_ok=True)
        return dest_path
    modification_time = item.capture_date
    year, month, day = (
        str(modification_time.year),
        modification_time.strftime("%B").capitalize(),
        str(modification_time.day),
    )
    # Determine the destination folder based on the sorting specification
    match sort_by:
        case "year":
            dest_folder = os.path.join(prefix, year)
        case "month":
            dest_folder = os.path.join(prefix, year, month)
        case _:
            dest_folder = os.path.join(prefix, year, month, day)
    os.makedirs(dest_folder, exist_ok=True)
    return os.path.join(dest_folder, item.basename)


def determine_originals(file_paths: list[str], num_keep: int) -> list[str]:
    """
    Given a list of file paths and the number of duplicates to keep,
    return a list of file paths that should be kept.

    Parameters:
    -----------
        - `file_paths (list[str])`: A list of file paths.
        - `num_keep (int)`: The number of duplicates to keep
    """
    oldest_to_newest = sorted(file_paths, key=lambda x: os.path.getmtime(x), reverse=False)
    keep = []
    remove = []
    for i, path in enumerate(oldest_to_newest):
        if i < MAX_DUPLICATES:
            keep.append(path)
        else:
            remove.append(path)
    return remove


def process_item(item: File, target_root: Dir, index, sort_by="month", dry_run=False) -> str | None:
    """
    Process a single item (file or directory) and move it to the appropriate destination folder.

    Paramaters:
    -------------
        - item (File): The media file to be sorted.
        - dest_folder (str): The base destination folder where the media will be placed.

    """
    dest_path = categorize_item(item, target_root, index, sort_by)
    if dest_path is not None:
        # Check for duplicates in the same directory, keeping MAX_DUPLICATES copies.
        count = 0
        existing_files = index.get(item.sha256(), [])
        while os.path.exists(dest_path):
            if len(existing_files) < MAX_DUPLICATES:
                # If there are less than the maximum number of duplicates, rename the file to avoid duplication.
                count += 1
                path, name = os.path.split(dest_path)
                dest_path = os.path.join(path, f"{count}-{name}")
            elif len(existing_files) > MAX_DUPLICATES:
                # If the maximum number of duplicates has been reached, determine if src is older than dest.
                # Then, remove the newer file, keeping the original.

                existing_files.append(item.path)
                overflow = sorted(existing_files, key=lambda x: os.path.getmtime(x))

                if args.dry_run:
                    cprint(f"[REMOVE] - {'\n'.join(overflow[MAX_DUPLICATES:])}")
                    cprint(f"[KEEP] - {'\n'.join(overflow[:MAX_DUPLICATES])}")
                    return None
                for file in overflow[MAX_DUPLICATES:]:
                    os.remove(file)
                return None
        try:
            shutil.move(item.path, dest_path, copy_function=shutil.copy2)
        except PermissionError as e:
            cprint.error(f"PermissionError: {e!r} {e.filename}")
            raise PermissionError from e
        except FileExistsError as e:
            cprint(f"{e.filename} | {e.filename2}")
        return dest_path
    return None


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
    index = dest.serialize() if refresh else dest.load_database()
    # If root and destination are the same, do not recurse into subdirectories
    file_objs = [obj(file) for file in path.content] if root == dest else path.file_objects
    pool = Pool()
    list(
        pool.execute(
            process_item,
            file_objs,
            progress_bar=True,
            dry_run=dry_run,
            index=index,
            target_root=dest,
            sort_by=spec,
        )
    )
    cleanup(root)
    try:
        os.rmdir(root)
    except OSError as e:
        print(f"{fg.red}Error{style.reset} {e.strerror}: {e.filename}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Take a directory tree and sort the contents by media type and date",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("ROOT", help="The top level directory to start sorting from")
    parser.add_argument("DEST", help="Destination folder for sorted files")
    parser.add_argument(
        "--spec",
        help="Spec file to use for sorting",
        choices=["year", "month", "day"],
        default="year",
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
    if os.path.exists(args.ROOT) and os.path.exists(args.DEST):
        main(args.ROOT, args.DEST, args.spec, args.refresh, args.dry_run)
    else:
        cprint.error("One or both of the provided paths do not exist.")
