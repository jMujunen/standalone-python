#!/usr/bin/env python3

import argparse
import os
import re
import shutil

from fsutils import Img, Video
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
        "-m",
        "--month",
        help="Sort into month directories",
        action="store_true",
        default=True,
        required=False,
    )
    parser.add_argument(
        "-y",
        "--year",
        help="Sort into year directories",
        action="store_true",
        default=False,
        required=False,
    )
    args = parser.parse_args()
    return args


def process_item(item: Video | Img, target_root: str) -> str | None:
    try:
        capture_date = item.capture_date
        year, month, day = (
            capture_date.year,
            capture_date.strftime("%B").capitalize(),
            capture_date.day,
        )
        dest_folder = os.path.join(target_root, str(year), month, str(day))
        dest_path = os.path.join(
            dest_folder, f'{capture_date.strftime("%H:%M.%S")}{item.extension}'
        )
        if not os.path.exists(dest_folder):
            os.makedirs(dest_folder, exist_ok=True)
        count = 1
        while os.path.exists(dest_path):
            dest_object = obj(dest_path)
            if item == dest_object:
                os.remove(item.path)
                break
            else:
                dest_path = os.path.join(
                    dest_folder, f'{capture_date.strftime("%H:%M.%S")}_{count}{item.extension}'
                )
                count += 1
        shutil.move(item.path, dest_path, copy_function=shutil.copy2)
        return item.basename
    except Exception as e:
        print(e)
    return


def main(root: str, dest: str) -> None:
    videos = Dir(root).videos
    pool = Pool()
    for result in pool.execute(process_item, videos, dest, progress_bar=True):
        if not result:
            print("\033[31mError\033[0m")


if __name__ == "__main__":
    args = parse_args()
    if os.path.exists(args.ROOT) and os.path.exists(args.DEST):
        main(args.ROOT, args.DEST)
    else:
        args.print_help()
