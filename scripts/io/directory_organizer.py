#!/usr/bin/env python3
"""Organize a directory by mimetype.

Additionally, creates an organized tree for any images or videos which get
sorted by capture date and moved to its respective folder"""

import argparse
import contextlib
import logging
import os
import re
import shutil
from collections.abc import Generator
from pathlib import Path
from re import Pattern

from Color import cprint, fg
from fsutils.dir import Dir, File
from fsutils.file import Base
from fsutils.utils.mimecfg import FILE_TYPES, IGNORED_DIRS
from ThreadPoolHelper import Pool

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

MAX_DUPLICATES = 2

DATE_REGEX: Pattern[str] = re.compile(
    r"\d{1,4}-(\d{4}).?(\d{2}).?(\d{2}).(\d{2}).?(\d{2}).?(\d{2})"
)


def cleanup(top: str) -> None:
    """Remove empty directories recursively with improved efficiency.
    This version attempts to remove directories only once, reducing redundant operations.
    """
    empty_dirs = set()

    # First pass: collect all empty directories
    for root, dirs, _ in os.walk(top, topdown=False):
        for d in dirs:
            dir_path = Path(root, d)
            try:
                if not any(dir_path.iterdir()):
                    empty_dirs.add(dir_path)
            except (PermissionError, OSError):
                continue

    # Second pass: remove empty directories
    for dir_path in sorted(empty_dirs, key=lambda p: len(str(p)), reverse=True):
        with contextlib.suppress(OSError):
            dir_path.rmdir()


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


def gen_stat(lst: list) -> Generator[zip[tuple], None, None]:
    """Generate statistics for pairs of items in the given list using the provided object function.
    Optimized version that caches file stats to avoid redundant file operations.

    Parameters
    ----------
        - `lst (list)`: A list of items to generate statistics for.

    Returns
    --------
        - `Generator[Tuple]`: A generator yielding tuples of statistics for each pair of items in the list.
    """
    # Cache file stats to avoid redundant operations
    file_cache = {}

    def get_file_times(path):
        if path not in file_cache:
            file_cache[path] = File(path).times()
        return file_cache[path]

    # Generate combinations more efficiently
    for i, item1 in enumerate(lst):
        for item2 in lst[i + 1 :]:
            yield zip(get_file_times(item1), get_file_times(item2), strict=False)


def determine_originals(file_paths: list[str], num_keep: int) -> set[str]:
    """Given a list of file paths and the number of duplicates to keep,
    return a list of file paths that should be removed.
    Optimized version with O(n log n) time complexity instead of O(n²).

    Parameters
    -----------
        - `file_paths (list[str])`: A list of file paths.
        - `num_keep (int)`: The number of duplicates to keep

    Returns
    --------
        - `set[str]`: A set of file paths that should be removed.
    """
    if not file_paths or len(file_paths) <= num_keep:
        return set()

    # Cache file stats to avoid redundant stat calls - O(n)
    file_stats = {}
    for path in file_paths:
        try:
            file_stats[path] = Path(path).stat().st_mtime
        except (FileNotFoundError, PermissionError):
            # Handle missing files gracefully
            file_stats[path] = float("inf")  # Consider missing files as newest

    # Sort files by modification time - O(n log n)
    sorted_paths = sorted(file_paths, key=lambda x: file_stats[x])

    # Keep the oldest num_keep files, mark the rest for removal
    return set(sorted_paths[num_keep:])


def process_item(
    item: Base,
    target_root: Dir,
    index: dict[str, list[str]],
    sort_spec: str,
    keep=False,
    dry_run=True,
    file_stats_cache: dict[str, float] = None,
) -> Path | None:
    """Process a single item (file or directory) and move it to the appropriate destination folder.
    Optimized version with caching and reduced file operations.

    Parameters
    -------------
        - item (Base): The media file to be sorted.
        - target_root (Dir): The root directory where all files will be moved.
        - index(dict): The hash index of existing files.
        - sort_spec(str): The sorting specification, either "day", "month" or "year".
        - keep(bool): Whether to keep the original file.
        - file_stats_cache(Dict): Cache for file modification times to avoid redundant stat calls.

    Returns
    ----------
        - Path: The path of the destination folder where the item was moved. None if no destination folder was found.
    """
    # Use a shared cache for file stats if provided
    file_stats_cache = file_stats_cache or {}

    # Get destination folder
    dest_folder = get_prefix(item=item, target=target_root.path, sort_spec=sort_spec)
    if dest_folder is None:
        return None

    # Create destination folder if it doesn't exist (with a single call)
    dest_folder.mkdir(parents=True, exist_ok=True)

    # Handle duplicates more efficiently
    file_hash = item.sha256()
    existing_files = index.get(file_hash, [])

    if len(existing_files) >= MAX_DUPLICATES:
        # Cache file stats to avoid redundant stat calls
        for file_path in existing_files:
            if file_path not in file_stats_cache:
                try:
                    file_stats_cache[file_path] = Path(file_path).stat().st_mtime
                except (FileNotFoundError, PermissionError):
                    file_stats_cache[file_path] = float(
                        "inf"
                    )  # Consider missing files as newest

        # Sort by modification time using cached values
        overflow = sorted(existing_files, key=lambda x: file_stats_cache[x])

        # Remove files exceeding MAX_DUPLICATES
        for file in overflow[MAX_DUPLICATES:]:
            try:
                if dry_run:
                    cprint(f"Would remove {file}", fg.red)
                else:
                    os.remove(file)
                    msg = f"Removed {file}"
                    cprint.error(msg)
            except (FileNotFoundError, PermissionError) as e:
                cprint.error(f"Error removing {file}: {e}")

    # Find a unique destination path efficiently
    dest_path = Path(dest_folder, item.name)
    if dest_path.exists():
        # Use a more efficient approach for finding a unique name
        base_name, ext = os.path.splitext(item.name)
        count = 1
        while True:
            new_name = f"{base_name}-{count}{ext}"
            dest_path = Path(dest_folder, new_name)
            if not dest_path.exists():
                break
            count += 1

    # Perform the file operation
    try:
        if keep:
            shutil.copy2(item.path, dest_path)
        else:
            shutil.move(item.path, dest_path, copy_function=shutil.copy2)

        # Update the index with the new file location
        if file_hash in index:
            index[file_hash].append(str(dest_path))
        else:
            index[file_hash] = [str(dest_path)]

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
    Optimized version with better memory usage and parallel processing.

    Parameters
    ----------
        - `root (str)`: The directory to start sorting from.
        - `destination (str)`: The directory to move sorted files into.
        - `spec (str)`: The file extension to sort by.
        - `refresh_db (bool)`: Whether or not to refresh the database.
        - `keep (bool)`: If true, do not delete the input directory (root)
    """
    path = Dir(root)
    dest = Dir(destination)
    root_object = Dir(root)

    # Load or create the destination index
    dest_index = dest.serialize(replace=refresh_db)

    # If root and destination are the same, do not recurse into subdirectories
    file_objs = (
        [File(file) for file in path.content]
        if root_object == dest
        else path.fileobjects()
    )

    # Format the sort specification
    sort_spec = sort_spec_formatter(spec)

    # Create a shared cache for file stats to reduce redundant file operations
    file_stats_cache = {}

    # Process files in batches for better memory efficiency
    num_moved = 0
    total_files = len(file_objs)

    # Use the existing Pool implementation but with optimized parameters
    pool = Pool()

    # Process files with the shared cache
    for result in pool.execute(
        function=process_item,
        data_source=file_objs,
        progress_bar=True,
        index=dest_index,
        target_root=dest,
        sort_spec=sort_spec,
        keep=keep,
        file_stats_cache=file_stats_cache,
    ):
        if result:
            num_moved += 1

    # Clean up if not keeping original files
    if not keep:
        print("Cleaning up empty directories...")
        cleanup(path.path)

        try:
            # Only try to remove the root directory if it exists and is empty
            root_path = Path(root)
            if root_path.exists() and not any(root_path.iterdir()):
                root_path.rmdir()
        except OSError as e:
            cprint.error(f"OSError while removing dir: {e.strerror}: {e.filename}")

    print(f"Moved {num_moved} files out of {total_files} files.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Take a directory tree and sort the contents by media type and date",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "ROOT", help="The top level directory to start sorting from", type=str
    )
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

    parser.add_argument(
        "--threads",
        help="Number of threads to use for processing",
        type=int,
        default=None,  # Will use default from ThreadPoolHelper
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
    import time

    start_time = time.time()

    args = parse_args()
    dest = args.dest
    root = args.ROOT
    spec = args.spec
    refresh = args.refresh

    # Ensure destination directory exists before running the script
    if not Path(args.dest).exists():
        Path(dest).mkdir(parents=True, exist_ok=True)

    print("Starting directory organization...")

    # Run the main function
    main(root, dest, spec, refresh, args.keep)

    # Print execution time
    elapsed_time = time.time() - start_time
    print(f"Total execution time: {elapsed_time:.2f} seconds")
    # main(
    #     "/mnt/ssd/staging/GALAXY_TABLET",
    #     "/mnt/hdd/Media/ELLA",
    #     "month",
    #     refresh_db=False,
    #     keep=True,
    # )
