#!/usr/bin/env python3
"""Organize a directory by mimetype.

Additionally, creates an organized tree for any images or videos which get
sorted by capture date and moved to its respective folder.
"""

import argparse
import os
import re
import shutil
from argparse import Namespace
from enum import Enum
from pathlib import Path
from re import Pattern

from Color import cprint
from fsutils.dir import Dir, File
from fsutils.file import Base
from fsutils.img import Img
from fsutils.utils.mimecfg import FILE_TYPES, IGNORED_DIRS
from fsutils.video import Video
from loggers import logger, logging
from ThreadPoolHelper import Pool

logger.setLevel(logging.INFO)
MAX_DUPLICATES = 2


DATE_REGEX: Pattern[str] = re.compile(
    r"\d{1,4}-(\d{4}).?(\d{2}).?(\d{2}).(\d{2}).?(\d{2}).?(\d{2})"
)


class SortSpec(Enum):
    """Date format specification for organizing media by capture date."""

    YEAR = "%Y"
    MONTH = "%Y/%h"
    DAY = "%Y/%h/%d"


def cleanup(top: str) -> None:
    """Remove empty directories recursively starting from the top.

    Args:
        top: Path to the root directory to clean.
    """
    for root, dirs, _ in os.walk(top, topdown=False):
        for d in dirs:
            Path(root, d).rmdir()
            logger.info(f"Removed empty dir: {root}/{d}")


def categorize_other(item: Base, target_root: str | Path) -> Path:
    """Move uncategorized files to the 'Other' directory based on mimetype.

    Args:
        item: File object to categorize.
        target_root: Root directory for the target structure.

    Returns
        Path to the categorized directory.
    """
    prefix = Path(target_root, "Other")
    for category, extensions in FILE_TYPES.items():
        if item.suffix.lower() in extensions:
            prefix = Path(prefix, category)
            break
    return prefix


def get_prefix(item: Base, target: str | Path, sort_spec: str) -> Path | None:
    """Determine the destination path for a file based on its type and capture date.

    Args:
        item: File object to sort.
        target: Root directory for the sorted files.
        sort_spec: Date format ('%Y' for year, '%Y/%m' for month, etc.)

    Returns
        Optional destination path or None if item should be ignored.
    """
    if item.suffix.lower() in FILE_TYPES["ignored"]:
        logger.info(f"Ignoring file: {item.name}")
        return None
    if item.suffix.lower() in FILE_TYPES["trash"]:
        try:
            Path(item.path).unlink()
            logger.debug(f"Removed trash file: {item.name}")
        except Exception as e:
            logger.error(f"Failed to remove trash file: {e}")
        return None
    for part in item.parts:
        if part in IGNORED_DIRS:
            logger.info(f"Ignoring directory: {part}")
            return None

    if isinstance(item, Img):
        if item.suffix.lower() == ".nef":
            prefix = Path(target, "Photos", "RAW", item.capture_date.strftime(sort_spec))
        prefix = Path(target, "Photos", item.capture_date.strftime(sort_spec))

    elif isinstance(item, Video):
        prefix = Path(target, "Videos", item.capture_date.strftime(sort_spec))

    elif isinstance(item, Dir):
        if not os.listdir(item.path):
            try:
                Path(item.path).unlink()
            except Exception as e:
                logger.error(f"Failed to remove empty src dir ({item.path}): {e}")
        return None
    else:
        prefix = categorize_other(item, target)
    return prefix


def get_next_available_path(dest_folder: Path, item: Base) -> Path:
    """Find the next available path for an item in a destination folder.

    Args:
        dest_folder: Destination directory.
        item: File object.

    Returns
        Path to the next available file name with a unique prefix.
    """
    existing_files = os.listdir(dest_folder)
    base_name = item.name
    pattern = re.compile(rf"(\d+)-{re.escape(base_name)}")

    max_count = 0
    for fname in existing_files:
        match = pattern.match(fname)
        if match:
            max_count = max(max_count, int(match.group(1)))
    return dest_folder / f"{f'{max_count}-' if max_count > 0 else ''}{base_name}"


def process_item(
    item: Base,
    dst: Dir,
    sort_spec: str,
    keep: bool = False,
    dry_run: bool = False,
    one_filesystem: bool = False,
) -> Path | None:
    """Process a single item and move/copy it to the appropriate destination folder.

    Args:
    ----
        item: File object to process.
        target_root: Target directory root.
        index: Hash map of existing file hashes and paths.
        sort_spec: Date format for sorting (year, month, day).
        keep: If True, copy instead of moving.
        dry_run: If True, do not actually move/copy files.
        one_filesystem: If True, use os.replace instead of shutil.copy

    Returns:
    -------
        Destination path if processed, None otherwise.
    """
    dest_folder = get_prefix(item=item, target=dst.path, sort_spec=sort_spec)
    if dest_folder is None:
        return None

    dest_folder.mkdir(parents=True, exist_ok=True)

    dest_path = Path(dest_folder / item.name)
    if dest_path.exists():
        dest_path = get_next_available_path(dest_folder, item)

    try:
        if dry_run:
            print(f"[DRY RUN] - Moving '{item.path}' to '{dest_path}'")
            return None
        if keep:
            logger.debug(f"Copying '{item.path}' to '{dest_path}'")
            shutil.copy2(item.path, dest_path)
        elif one_filesystem:
            logger.debug(f"Moving '{item.path}' to '{dest_path}'")
            os.replace(item.path, dest_path)
        else:
            logger.debug(f"Moving '{item.path}' to '{dest_path}'")
            shutil.move(item.path, dest_path, copy_function=shutil.copy2)
        return dest_path
    except PermissionError as e:
        cprint.error(f"Permission denied: {e!r}")
        return None
    except Exception as e:
        cprint.error(f"Unidentified error: {e!r}: {item.path} -> {dest_path}")
        return None


def main(
    src: str,
    dst: str,
    spec: str,
    keep: bool,
    dry_run: bool,
    one_filesystem: bool = False,
) -> None:
    """Sort files by media type and capture date.

    Args:
        root: Root directory to start sorting from.
        dst: Target root directory for sorted files.
        spec: Sort specification: 'year', 'month', or 'day'.
        refresh_db: Whether to refresh the index if it exists.
        keep: If True, keep original files in source.
    """
    dest_dir = Dir(dst)
    root_dir = Dir(src)

    # If root and destination are the same, do not recurse into subdirectories
    file_objs = (
        [File(file) for file in root_dir.content]
        if root_dir == dest_dir
        else root_dir.fileobjects()
    )

    pool = Pool()
    num_moved = 0

    for result in pool.execute(
        process_item,
        file_objs,
        progress_bar=True,
        dst=dest_dir,
        sort_spec=spec,
        keep=keep,
        dry_run=dry_run,
        one_filesystem=one_filesystem,
    ):
        if result:
            num_moved += 1

    if not keep:
        cleanup(root_dir.path)

        try:
            Path(src).rmdir()
        except OSError as e:
            cprint.error(f"OSError while removing dir: {e.strerror}: {e.filename}")

    print(f"Moved {num_moved} files out of {len(file_objs)} files.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Take a directory tree and sort the contents by media type and date.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "src", help="The top level directory to start sorting from", type=str
    )

    parser.add_argument(
        "dst",
        help="Destination folder for sorted files.",
        type=str,
    )

    parser.add_argument(
        "--spec",
        help="Spec file to use for sorting.",
        choices=["year", "month", "day"],
        default="month",
    )

    parser.add_argument(
        "--keep",
        help="Do not delete src files after sorting.",
        action="store_true",
    )

    parser.add_argument(
        "--dry-run",
        help="Print actions instead of performing them",
        action="store_true",
    )

    parser.add_argument(
        "-1",
        "--one-filesystem",
        help="Setting this flag forces the use of os.rename() instead of shutil.move() for faster operations",
        action="store_true",
    )

    return parser.parse_args()


if __name__ == "__main__":
    import sys

    args: Namespace = parse_args()
    src = args.src
    dst = args.dst
    spec = SortSpec[args.spec.upper()].value
    keep = args.keep
    dry_run = args.dry_run
    one_filesystem = args.one_filesystem

    if not Path(src).exists():
        print(f"\033[31mError:\033[0m  {src} does not exist.")
        sys.exit(1)
    if not Path(dst).exists():
        Path(dst).mkdir(parents=True, exist_ok=True)
    main(
        src=src,
        dst=dst,
        spec=spec,
        keep=keep,
        dry_run=dry_run,
        one_filesystem=one_filesystem,
    )
