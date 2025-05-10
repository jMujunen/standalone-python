#!/usr/bin/env python3
"""Sort all videos and/or images in a given directory into specfified structure.

Example:
--------
>>> ./dir_sort.py /media/ /mnt/ssd/media/ --level day
"""

import argparse
import datetime
import os
import re
import shutil
from pathlib import Path

from fsutils.dir import Dir, obj
from fsutils.file import File
from fsutils.img import Img
from fsutils.video import Video
from ThreadPoolHelper import Pool

DATE_REGEX = re.compile(r"\d{1,4}-(\d{4}).?(\d{2}).?(\d{2}).(\d{2}).?(\d{2}).?(\d{2})")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Take a directory tree and sort the contents by media type and date"
    )
    parser.add_argument("ROOT", help="The top level directory to start sorting from")
    parser.add_argument("DEST", help="Destination folder for sorted files")
    parser.add_argument(
        "--level",
        choices=["day", "month", "year"],
        help="Specify the sorting level to use",
        default="day",
        required=False,
    )
    parser.add_argument(
        "--rename",
        help="Change file name to date based off mtime",
        default=False,
        action="store_true",
    )
    return parser.parse_args()


def process_item(item: File, target_root: str, rename=True) -> str | None:
    """Move a file to the specified destination folder.

    Paramaters:
    -----------
        - item (File): The file object to be moved.
        - target_root (str): The destination folder where the file will be placed.
        - rename (bool) :

    Returns
    ---------
        - str: The new name of the file after moving, or its original name if renaming is not requested.

    """
    match item:
        case Img() | Video():
            modification_time = item.capture_date
        case Dir():
            return os.remove(item.path) if item.is_empty else None
        case _:
            modification_time = item.mtime
    year, month, day = (
        modification_time.year,
        modification_time.strftime("%B").capitalize(),
        modification_time.day,
    )  # type : ignore
    dest_folder = os.path.join(target_root, str(year), month, str(day))
    # Rename the file to include time of capture if cli flag is set
    if rename:
        dest_path = os.path.join(
            dest_folder,
            f"{modification_time.strftime('%H:%M.%S')}{item.suffix}",
        )
    else:
        dest_path = os.path.join(dest_folder, item.name)
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder, exist_ok=True)
    count = 1
    while os.path.exists(dest_path):
        dest_object = obj(dest_path)
        # Keep destination file, remove source file if they are duplicate
        if item == dest_object:
            os.remove(item.path)
            break
        dest_path = os.path.join(
            dest_folder,
            f"{modification_time.strftime('%H:%M.%S')}_{count}{item.suffix}",
        )
        count += 1
    shutil.move(item.path, dest_path, copy_function=shutil.copy2)
    return item.name


def main(videos: list[Video], dest: str) -> None:
    pool = Pool()
    for result in pool.execute(process_item, list(videos), target_root=dest):
        if not result:
            print("\033[31mError\033[0m")


class args:
    ROOT = "/mnt/hdd/webcam"
    DEST = "/mnt/hdd/sorted-webcam-clips"


if __name__ == "__main__":
    args = parse_args()
    source = Dir(args.ROOT)
    dest = Dir(args.DEST)
    if source.path == dest.path:
        videos = [
            obj(os.path.join(source.path, i))
            for i in source.content
            if i.lower().endswith((".mp4", ".mov", "mkv"))
        ]
    else:
        videos = source.videos()
    main(videos, args.DEST)
