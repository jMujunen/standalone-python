#!/usr/bin/env python3
"""Organize a directory by mimetype. Additionally, creates an organized tree for
    for any images or videos which get sorted by capture date and moved to its respective folder"""

import argparse
import datetime
import os
import re
import shutil
from pathlib import Path

from Color import cprint, fg
from fsutils import File, Img, Video
from fsutils.DirNode import Dir, obj
from ThreadPoolHelper import Pool

DATE_REGEX = re.compile(r"\d{1,4}-(\d{4}).?(\d{2}).?(\d{2}).(\d{2}).?(\d{2}).?(\d{2})")


def cleanup(top) -> None:
    for root, dirs, files in os.walk(top):
        for d in dirs:
            cleanup(os.path.join(root, d))
        if not dirs and not files:
            os.rmdir(root)


def detect_duplicates(src_object: File, dest_filepath: str) -> str:
    count = 0
    while os.path.exists(dest_filepath):
        dest_object = obj(dest_filepath)
        if src_object == dest_object:
            # If the file is identical, remove it from its original location
            os.remove(src_object.path)
            break
        # If the file exists but isn't identical, generate a new name for it
        dest_filepath = os.path.join(dest_object.path, f"{count}-{src_object.basename}")
        count += 1
    else:
        # If the file is not identical or doesn't exist yet, move it to its new location
        shutil.move(src_object.path, dest_filepath)
    return src_object.basename


def process_item(item: File, target_root: str, sort_by="month") -> str | None:
    """
    Sort a media file into the appropriate destination folder based on its type and creation date.

    Paramaters:
        item (File): The media file to be sorted.
        dest_folder (str): The base destination folder where the media will be placed.

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

    modification_time = item.capture_date  # Get the modification time of the file
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
    path = Dir(root)
    file_objs = [obj(file) for file in path.content] if root == dest else path.file_objects
    pool = Pool()
    for result in pool.execute(process_item, file_objs, dest, spec, progress_bar=True):
        if not result:
            print("\033[31mError\033[0m")
    cleanup(root)
    os.rmdir(root)


if __name__ == "__main__":
    args = parse_args()
    if os.path.exists(args.ROOT) and os.path.exists(args.DEST):
        main(args.ROOT, args.DEST, args.spec)
    else:
        args.print_help()
