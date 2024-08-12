#!/usr/bin/env python3

import argparse
import datetime
import os
import re
import shutil
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

from fsutils import Dir, File, Img, Video
from ProgressBar import ProgressBar

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


def process_item(item: Video | Img, target_root: str) -> tuple[datetime.datetime, File]:
    capture_date = item.capture_date
    year, month, day = capture_date.year, capture_date.strftime("%B").capitalize(), capture_date.day
    dest = os.path.join(target_root, str(year), month, str(day))
    if not os.path.exists(dest):
        os.makedirs(dest)
    shutil.move(item.path, dest)
    # try:
    #     creation_date = item.__getattribute__("capture_date")
    #     return creation_date, item
    # except AttributeError:
    #     creation_date = str(datetime.datetime.fromtimestamp(os.path.getmtime(item.path))).split(
    #         "."
    #     )[0]
    # return datetime.datetime.fromisoformat(creation_date), item


def month_sort(file: File, file_date: datetime.datetime, dest: str) -> None:
    try:
        if not os.path.exists(dest):
            os.makedirs(dest)
        month_folder = os.path.join(dest, int_to_month(file_date.month))
        os.makedirs(month_folder, exist_ok=True)
        shutil.move(
            file.path, os.path.join(month_folder, file.basename), copy_function=shutil.copy2
        )
    except Exception as e:
        print(e)


def day_sort(file: File, file_date: datetime.datetime, dest: str) -> None:
    try:
        if not os.path.exists(dest):
            os.makedirs(dest)
        days_folder = os.path.join(dest, (file_date.strftime("%d")))
        os.makedirs(days_folder, exist_ok=True)
        day_folder = os.path.join(days_folder, file_date.strftime("%d"))
        os.makedirs(day_folder, exist_ok=True)
        shutil.move(
            file.path,
            os.path.join(day_folder, file.basename),
            copy_function=shutil.copy2,
        )
    except Exception as e:
        print(e)


def main(top: str, dest: str) -> None:
    topmost = Dir(top).content
    with ProgressBar(len(topmost)) as progress:
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(process_item, item) for item in topmost]
            for future in as_completed(futures):
                result = future.result()
                progress.increment()
                if result:
                    date, item = result
                    month_sort(item, date, dest)


if __name__ == "__main__":
    args = parse_args()
    if os.path.exists(args.ROOT) and os.path.exists(args.DEST):
        main(args.ROOT, args.DEST)
    else:
        args.print_help()
