#!/usr/bin/env python3
"""Organize a directory by mimetype.

Additionally, creates an organized tree for any images or videos which get
sorted by capture date and moved to its respective folder"""

import argparse
import contextlib
import os
import re
import shutil
from argparse import Namespace
from collections import defaultdict
from enum import Enum
from pathlib import Path
from re import Pattern

from Color import cprint, fg
from fsutils.dir import Dir, File
from fsutils.file import Base
from fsutils.utils.mimecfg import FILE_TYPES, IGNORED_DIRS
from ThreadPoolHelper import Pool

MAX_DUPLICATES = 2

DATE_REGEX: Pattern[str] = re.compile(
    r"\d{1,4}-(\d{4}).?(\d{2}).?(\d{2}).(\d{2}).?(\d{2}).?(\d{2})"
)


class SortSpec(Enum):
    YEAR = "%Y"
    MONTH = "%Y/%h"
    DAY = "%Y/%h/%d"


def cleanup(top: str) -> None:
    """Remove empty directories recursively."""
    for root, dirs, _ in os.walk(top, topdown=False):
        for d in dirs:
            Path(root, d).rmdir()


def categorize_other(y: Base, x: str | Path) -> Path:
    """Move files that are not categorized to the other directory based of mimetype.

    Paramaters:
    -----------
        - item (Base): The file object.
        - target_root (Dir): The target root directory
    """
    prefix = Path(x, "Other")
    for k, v in FILE_TYPES.items():
        if y.suffix.lower() in v:
            prefix = Path(prefix, k)
    return prefix


def get_prefix(item: Base, target: str, sort_spec: str) -> Path | None:
    """Categorize a Base into the appropriate destination folder based on its type and creation date.

    Parameters
    ----------
        - item (Base): The file object.
        - target (str): The target directory path.
        - sort_spec (str): The sorting specification, e.g., 'year', 'month', 'day'

    Returns
    -------
        - Path | None: The destination path for the file or None if it should be ignored.
    """
    if item.suffix.lower() in FILE_TYPES["trash"]:
        Path(item.path).unlink()
        cprint.info(f"Removed {item.name}")
        return None
    for part in item.parts:
        if part in IGNORED_DIRS:
            return None

    match item.__class__.__name__:
        case "Img":
            return (
                Path(target, "Photos", item.capture_date.strftime(sort_spec))  # type: ignore
                if item.suffix.lower() != ".nef"
                else Path(
                    target,
                    "Photos",
                    "RAW",
                    item.capture_date.strftime(sort_spec),  # type: ignore
                )
            )
        case "Video":
            return Path(
                target,
                "Videos",
                item.capture_date.strftime(sort_spec),  # type: ignore
            )
        case "Dir":
            return Path(item.path).unlink() if not os.listdir(item.path) else None
        case _:
            return categorize_other(item, target)


def determine_originals(file_paths: list[str], num_keep: int) -> set[str]:
    """Given a list of file paths and the number of duplicates to keep,
    return a list of file paths that should be removed.

    Parameters
    -----------
        - `file_paths (list[str])`: A list of file paths.
        - `num_keep (int)`: The number of duplicates to keep

    Returns
    --------
        - `set[str]`: A set of file paths that should be removed.
    """
    hash_map = defaultdict(list)

    # Group files by their SHA-256 hash
    for path in file_paths:
        try:
            sha256_hash = File(path).sha256()
            hash_map[sha256_hash].append(path)
        except Exception as e:
            cprint.warn(f"Error hashing {path}: {e}")

    remove_set = set()
    for paths in hash_map.values():
        if len(paths) <= num_keep:
            continue
        # Sort by modification time (oldest first)
        sorted_paths = sorted(paths, key=lambda p: Path(p).stat().st_mtime)
        # Remove the newest ones beyond num_keep
        remove_set.update(sorted_paths[num_keep:])

    return remove_set


def get_next_available_path(dest_folder: Path, item: Base) -> Path:
    """Find the next available path for an item in a destination folder.

    Parameters
    ----------
        - `dest_folder (Path)`: The destination folder where the item will be placed.
        - `item (Base)`: The item to find a path for.

    Returns
    ---------
        - `Path`: The next available path for the item.
    """
    existing_files = os.listdir(dest_folder)
    base_name = item.name
    pattern = re.compile(rf"(\d+)-{re.escape(base_name)}")

    max_count = 0
    for fname in existing_files:
        match = pattern.match(fname)
        if match:
            max_count = max(max_count, int(match.group(1)))

    return dest_folder / f"{max_count + 1}-{base_name}"


def process_item(
    item: Base,
    target_root: Dir,
    index: dict[str, list[str]],
    sort_spec: str,
    keep=False,
) -> Path | None:
    """Process a single item (file or directory) and move it to the appropriate destination folder.

    Paramaters:
    -------------
        - item (Base): The media file to be sorted.
        - target_root (Dir): The root directory where all files will be moved.
        - index(int): The current index of the item in the list of items.
        - sort_spec(str): The sorting specification, either "day", "month" or "year".

    Returns
    ----------
        - Path: The path of the destination folder where the item was moved. None if no destination folder was found.
    """
    dest_folder = get_prefix(item=item, target=target_root.path, sort_spec=sort_spec)
    if dest_folder is None:
        return None
    if not dest_folder.exists():
        dest_folder.mkdir(parents=True, exist_ok=True)
    dest_path = Path(dest_folder, item.name)

    # Check for duplicates in the same directory, keeping MAX_DUPLICATES copies.
    count = 0
    existing_files = index.get(item.sha256(), [])
    while dest_path.exists():
        with contextlib.suppress(FileNotFoundError, FileExistsError):
            # cprint.warn(f"Base {item.name} already exists in destination directory.")
            if len(existing_files) < MAX_DUPLICATES:
                # Rename the file while under MAX_DUPLICATES
                count += 1
                path, _ = os.path.split(dest_path)
                dest_path = Path(path, f"{count}-{item.name}")
            elif len(existing_files) > MAX_DUPLICATES:
                # Remove newest items while MAX_DUPLICATES is exceeded.
                existing_files.append(item.path)
                overflow = sorted(existing_files, key=lambda x: Path(x).stat().st_mtime)
                # if dry_run:
                cprint(
                    f"[REMOVE] - {'\n'.join(overflow[MAX_DUPLICATES:])}",
                    fg.deeppink,
                )
                cprint(f"[KEEP] - {'\n'.join(overflow[:MAX_DUPLICATES])}", fg.cyan)
                # return None
                for file in overflow[MAX_DUPLICATES:]:
                    # if dry_run is True:
                    # else:
                    msg = f"Removed {file}"
                    cprint.error(msg)
                    os.remove(file)
            else:
                # If there are no duplicates or the number of copies is under control, just return.
                break
    with contextlib.suppress(FileExistsError, FileNotFoundError):
        try:
            if keep:
                shutil.copy2(item.path, dest_path)
            else:
                shutil.move(item.path, dest_path, copy_function=shutil.copy2)
            return dest_path
        except PermissionError as e:
            msg = f"{e!r}"
            cprint.error(msg)
            return None
        except Exception as e:
            msg = f"Unidentified Error: {e!r}: {item.path} {dest_path}"
            cprint.error(msg)
            return dest_path


def main(root: str, destination: str, spec: str, refresh_db: bool, keep: bool) -> None:
    """Sort files based on media type and date.

    Paramaters:
    ----------
        - `root (str)`: The directory to start sorting from.
        - `destination (str)`: The directory to move sorted files into.
        - `spec (str)`: The file extension to sort by.
        - `refresh (bool)`: Whether or not to refresh the database.
        - `keep (bool)`: If true, do not delete the input directory (root)
    """
    path = Dir(root)
    dest = Dir(destination)
    root_object = Dir(root)

    dest_index = dest.serialize(replace=refresh_db)

    # If root and destination are the same, do not recurse into subdirectories
    file_objs = [File(file) for file in path.content] if root_object == dest else path.fileobjects()

    sort_spec = SortSpec[spec.capitalize()]
    pool = Pool()
    num_moved = 0

    for result in pool.execute(
        process_item,
        file_objs,
        progress_bar=True,
        index=dest_index,
        target_root=dest,
        sort_spec=sort_spec,
        keep=keep,
    ):
        if result:
            num_moved += 1

    if not keep:
        cleanup(path.path)

        try:
            Path(root).rmdir()
        except OSError as e:
            cprint.error(f"OSError while removing dir: {e.strerror}: {e.filename}")

    print(f"Moved {num_moved} files out of {len(file_objs)} files.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Take a directory tree and sort the contents by media type and date",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("ROOT", help="The top level directory to start sorting from", type=str)
    parser.add_argument(
        "--dest",
        help="Destination folder for sorted files",
        type=str,
        default="./sorted",
    )
    parser.add_argument(
        "--spec",
        help="Spec file to use for sorting",
        choices=["year", "month", "day"],
        default="month",
    )
    parser.add_argument(
        "-f",
        "--filter",
        help="Only sort this type of file",
        choices=["img", "video", "file"],
    )
    parser.add_argument(
        "--refresh",
        help="Refresh the index even if it exists",
        action="store_true",
        default=False,
        required=False,
    )
    parser.add_argument(
        "--keep",
        help="Keep original files in their directories",
        action="store_true",
        default=False,
        required=False,
    )

    # parser.add_argument(
    #     "--dry-run",
    #     help="Print actions instead of performing them",
    #     action="store_true",
    #     default=False,
    #     required=False,
    # )
    return parser.parse_args()


if __name__ == "__main__":
    args: Namespace = parse_args()
    dest = args.dest
    root = args.ROOT
    spec = args.spec
    refresh = args.refresh
    keep = args.keep
    # Ensure destination directory exists before running the script
    if not Path(dest).exists():
        Path(dest).mkdir(parents=True, exist_ok=True)
    print(f"Keep : {keep}, Update Index: {refresh}")
    main(root, dest, spec, refresh, keep)
