#!/usr/bin/env python3
"""Organize a directory by mimetype.

Additionally, creates an organized tree for any images or videos which get
sorted by capture date and moved to its respective folder"""

import argparse
import itertools
import os
import re
import shutil
import sys
from collections.abc import Generator
from pathlib import Path
from typing import Any

from Color import cprint, fg
from fsutils.dir import Dir, obj
from fsutils.file import File
from fsutils.utils import FILE_TYPES, IGNORED_DIRS
from ThreadPoolHelper import Pool

MAX_DUPLICATES = 2

DATE_REGEX = re.compile(r"\d{1,4}-(\d{4}).?(\d{2}).?(\d{2}).(\d{2}).?(\d{2}).?(\d{2})")


def cleanup(top: Path) -> None:
    """Remove empty directories recursively."""
    for root, dirs, files in os.walk(top):
        for d in dirs:
            cleanup(Path(root, d))
        if not dirs and not files:
            Path(root).rmdir()


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


def categorize_other(y: File, x: str | Path) -> Path:
    """Move files that are not categorized to the other directory based of mimetype.

    Paramaters:
    -----------
        - item (File): The file object.
        - target_root (Dir): The target root directory
    """
    prefix = Path(x, "Other")
    for k, v in FILE_TYPES.items():
        if y.suffix.lower() in v:
            prefix = Path(prefix, k)
    return prefix


def get_prefix(item: File, target: str, sort_spec: str) -> Path | None:
    """Categorize a file into the appropriate destination folder based on its type and creation date.

    Parameters
    ----------
        - item (File): The file object.
        - target (str): The target directory path.
        - sort_spec (str): The sorting specification, e.g., 'year', 'month', 'day'
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
            return item.unlink() if not os.listdir(item.path) else None
        case _:
            return categorize_other(item, target)


def gen_stat(lst: list) -> Generator[zip]:
    for item in itertools.combinations(lst, 2):
        pair = obj(item[0]), obj(item[1])
        yield zip(*(p.stat()[-3:] for p in pair), strict=False)


def determine_originals(file_paths: list[str], num_keep: int) -> set[str]:
    """Given a list of file paths and the number of duplicates to keep,
    return a list of file paths that should be removed.

    Parameters
    -----------
        - `file_paths (list[str])`: A list of file paths.
        - `num_keep (int)`: The number of duplicates to keep
    """
    oldest_to_newest = sorted(file_paths, key=lambda x: Path(x).stat().st_mtime, reverse=False)
    keep = []
    remove = []
    for i, path in enumerate(oldest_to_newest):
        if i < num_keep:
            keep.append(path)
        else:
            for st_result in gen_stat(oldest_to_newest):
                for st in st_result:
                    if st[0] != st[1] and st[0] < st[1]:
                        break
                remove.append(path)
    return set(remove)


def process_item(
    item: File, target_root: Dir, index: dict[str, list[str]], sort_spec: str, keep=False
) -> Path | None:
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
    if not dest_folder.exists():
        dest_folder.mkdir(parents=True, exist_ok=True)
    dest_path = Path(dest_folder, item.name)

    # Check for duplicates in the same directory, keeping MAX_DUPLICATES copies.
    count = 0
    existing_files = index.get(item.sha256(), [])
    while dest_path.exists():
        cprint.warn(f"File {item.name} already exists in destination directory.")
        if len(existing_files) < MAX_DUPLICATES:
            # Rename the file while under MAX_DUPLICATES
            count += 1
            path, name = os.path.split(dest_path)
            dest_path = Path(path, f"{count}-{item.name}")
        elif len(existing_files) > MAX_DUPLICATES:
            # Remove newest items while MAX_DUPLICATES is exceeded.
            existing_files.append(item.path)
            overflow = sorted(existing_files, key=lambda x: Path(x).stat().st_mtime)
            # if dry_run:
            cprint(f"[REMOVE] - {"\n".join(overflow[MAX_DUPLICATES:])}", fg.deeppink)
            cprint(f"[KEEP] - {"\n".join(overflow[:MAX_DUPLICATES])}", fg.cyan)
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
    try:
        if keep:
            shutil.copy2(item.path, dest_path)
        else:
            shutil.move(item.path, dest_path, copy_function=shutil.copy2)
    except (PermissionError, FileExistsError, FileNotFoundError) as e:
        msg = f"{e}: {e.filename} {e.filename2}"
        cprint.error(msg)
        raise e from e
    except Exception as e:
        msg = f"Unidentified Error: {e!r}: {item.path} {dest_path}"
        cprint.error(msg)
        return dest_path


def filter_files(root: Dir, filter_spec: str) -> list[File]:
    """Filter files based on a given specification."""
    filter_spec = filter_spec.capitalize()
    module = sys.modules[__name__]
    FileClass = getattr(module, filter_spec)
    return [item for item in root if isinstance(item, FileClass)]


def main(root: str, destination: str, spec: str, refresh_db=False, keep=False) -> None:
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
    index = dest.serialize(replace=refresh_db)
    # If root and destination are the same, do not recurse into subdirectories
    file_objs = [obj(file) for file in path.content] if root_object == dest else path.file_objects
    sort_spec = sort_spec_formatter(spec)
    pool = Pool()
    list(
        pool.execute(
            process_item,
            file_objs,
            progress_bar=True,
            index=index,
            target_root=dest,
            sort_spec=sort_spec,
            keep=keep,
        )
    )

    if not keep:
        cleanup(path)

    try:
        path.rmdir()
    except OSError as e:
        cprint.error(f"OSError while removing dir: {e.strerror}: {e.filename}")


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
        "--use-index",
        help="Instead of indexing the target directory from scratch, use the existing directory .pkl file as the index",
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
    args = parse_args()
    dest = Path(args.dest)
    root = args.ROOT
    spec = args.spec
    refresh_db = not args.use_index

    # Ensure destination directory exists before running the script
    if not dest.exists:
        dest.mkdir(parents=True, exist_ok=True)
    main(root, dest, spec, refresh_db, args.keep)
