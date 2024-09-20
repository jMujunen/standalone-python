#!/usr/bin/env python3
"""Sort all videos and/or images in a given directory into specfified structure.

Example:
--------
>>> ./dir_sort.py /media/ /mnt/ssd/media/ --level day

outputs

2024
├── August
│   ├── 10
│   ├── 11
├── July
│   └── 14
└── September
    ├── 1
"""

import argparse
import datetime
import os
import re
import shutil

from fsutils import File, Img, Video
from fsutils.DirNode import Dir, obj
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
        help="Specifys the sorting level to use",
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
    """
    Move a file to the specified destination folder and renames it if requested.

    Paramaters:
        - item (File): The file object to be moved.
        - dest_folder (str): The destination folder where the file will be placed.

    Returns:
        - str: The new name of the file after moving, or its original name if renaming is not requested.

    This function handles the logic for moving a file to a specified destination folder and optionally renames it based on its modification time.
    Duplicates are removed, favouring the destination folder and removing from the source folder.
    """
    if isinstance(item, Img | Video):
        modification_time = item.capture_date
    elif isinstance(item, Dir):
        # Remove the dir if empty
        if item.is_empty:
            os.rmdir(item.path)
        return None
    else:
        modification_time = datetime.datetime.fromtimestamp(os.stat(item.path).st_mtime)

    year, month, day = (
        modification_time.year,
        modification_time.strftime("%B").capitalize(),
        modification_time.day,
    )  # type : ignore
    dest_folder = os.path.join(target_root, str(year), month, str(day))
    # Rename the file to include time of capture if cli flag is set
    if rename:
        dest_path = os.path.join(
            dest_folder, f'{modification_time.strftime("%H:%M.%S")}{item.extension}'
        )
    else:
        dest_path = os.path.join(dest_folder, item.basename)
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
            dest_folder, f'{modification_time.strftime("%H:%M.%S")}_{count}{item.extension}'
        )
        count += 1
    shutil.move(item.path, dest_path, copy_function=shutil.copy2)
    return item.basename


def main(root: str, dest: str) -> None:
    path = Dir(root)
    if root == dest:
        videos = [
            obj(os.path.join(path.path, i))
            for i in path.content
            if i.endswith((".mp4", ".mov", "mkv"))
        ]
    else:
        videos = Dir(root).videos
    pool = Pool()
    for result in pool.execute(process_item, list(videos), dest, progress_bar=True):
        if not result:
            print("\033[31mError\033[0m")


if __name__ == "__main__":
    args = parse_args()
    # if os.path.exists(args.ROOT) and os.path.exists(args.DEST):
    main(args.ROOT, args.DEST)
