#!/usr/bin/env python3
"""Organize a directory by mimetype.

Additionally, creates an organized tree for any images or videos which get
sorted by capture date and moved to its respective folder"""

import argparse
import datetime
import os
import re
import shutil
from pathlib import Path

from Color import Logger, cprint, fg, style
from fsutils import File, Img, Video
from fsutils.DirNode import Dir, obj
from ThreadPoolHelper import Pool

DATE_REGEX = re.compile(r"\d{1,4}-(\d{4}).?(\d{2}).?(\d{2}).(\d{2}).?(\d{2}).?(\d{2})")

logger = Logger()


def cleanup(top) -> None:
    """Remove empty directories recursively."""
    for root, dirs, files in os.walk(top):
        for d in dirs:
            cleanup(os.path.join(root, d))
        if not dirs and not files:
            os.rmdir(root)


def detect_duplicates(src_object: File, dest_filepath: str):  # -> str:
    """Detect if a duplicate exists and returns a unique filename."""
    count = 0
    while os.path.exists(dest_filepath):
        dest_object = obj(dest_filepath)
        if src_object == dest_object:
            # If the file is identical, remove it from its original location
            msg = f"{src_object.basename} already exists at {dest_filepath}. Removing {fg.orange}{src_object.basename}{style.reset}"
            logger.warning(msg)
            try:
                os.remove(src_object.path)
            except OSError as e:
                logger.error(f"{e!r}: Run as root", end="\r")
                return None
            return None
            os.remove(src_object.path)
            break
        #     # If the file exists but isn't identical, generate a new name for it
        dest_filepath = os.path.join(dest_object.path, f"{count}-{src_object.basename}")
        count += 1
    # else:
    #     # If the file is not identical or doesn't exist yet, move it to its new location
    #     shutil.move(src_object.path, dest_filepath)
    # return src_object.basename
    try:
        shutil.move(src_object.path, dest_filepath)
    except PermissionError as e:
        logger.error(f"PermissionError: {e!r}")
        raise PermissionError from e
    return src_object.basename


def process_item(item: File, target_root: str, sort_by="month") -> str | None:
    """
    Categorize a file into the appropriate destination folder based on its type and creation date.

    Paramaters:
    -------------
        - item (File): The media file to be sorted.
        - dest_folder (str): The base destination folder where the media will be placed.

    """
    if isinstance(item, Img):
        prefix = os.path.join(target_root, "Pictures")
    # Set the destination folder to Videos for video files
    elif isinstance(item, Video):
        prefix = os.path.join(target_root, "Videos")
    elif isinstance(item, Dir):
        # Remove the directory if it's empty
        if item.is_empty:
            os.rmdir(item.path)
        return None
    else:
        # Set the destination folder to Other for other types of files
        prefix = os.path.join(target_root, "Other")
        dest_path = os.path.join(prefix, item.basename)
        if not os.path.exists(prefix):
            os.makedirs(prefix, exist_ok=True)
        return detect_duplicates(item, dest_path)

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

    dest_path = os.path.join(dest_folder, item.basename)
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder, exist_ok=True)
    return detect_duplicates(item, dest_path)


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
    return parser.parse_args()


def main(root: str, dest: str, spec: str) -> None:
    """Sort files based on media type and date."""
    path = Dir(root)
    # If root and destination are the same, do not recurse into subdirectories
    file_objs = [obj(file) for file in path.content] if root == dest else path.file_objects
    pool = Pool()
    list(pool.execute(process_item, file_objs, dest, spec, progress_bar=False))
    cleanup(root)
    try:
        os.rmdir(root)
    except OSError as e:
        print(f"{fg.red}Error{style.reset} {e.strerror}: {e.filename}")


if __name__ == "__main__":
    args = parse_args()
    if os.path.exists(args.ROOT) and os.path.exists(args.DEST):
        main(args.ROOT, args.DEST, args.spec)
    else:
        args.print_help()
