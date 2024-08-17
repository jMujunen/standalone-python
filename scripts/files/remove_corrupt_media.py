#!/usr/bin/env python3
"""Finds and removes corrupt images and videos."""

import argparse
import os

from Color import cprint, fg, style
from ExecutionTimer import ExecutionTimer
from fsutils import Dir, Img, Video
from ProgressBar import ProgressBar
from ThreadPoolHelper import Pool


def parse_arguments():
    parser = argparse.ArgumentParser(description="Finds and removes corrupt images and videos")
    parser.add_argument("path", help="Path to the directory")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Do not remove files, only show what would be done",
    )
    return parser.parse_args()


def process_file(item: Img | Video):
    return (item.is_corrupt, item.path)


def main(path: str, dry_run: bool) -> None:
    pool = Pool()
    corrupted_files = []

    images = Dir(path).images
    videos = Dir(path).videos
    num_images = len(images)
    num_videos = len(videos)

    media = images + videos
    num_media = num_videos + num_images
    cprint(f"{num_images} images, {num_videos} videos", fg.green, style.bold)
    for result in pool.execute(process_file, media, progress_bar=True):
        corrupt, path = result
        if corrupt:
            print(f"{len(corrupted_files)}/{num_media} corrupt...", end="\r")
            corrupted_files.append(path)
            # if not args.dry_run:
            #     try:
            #         os.remove(path)
            #     except OSError:
            #         pass
            #     except Exception as e:
            #         cprint(e, fg.red)
            # else:
            # if len(corrupted_files) % 10 == 0:
            #     with open(f"{path}_CORRUPT_FILES.log", "w") as f:
            #         f.write("\n".join(corrupted_files))
    if not dry_run and corrupted_files:
        print("\n".join(corrupted_files))
        if input("Are you sure you want to remove these files? [y/N]: ") in [
            "y",
            "Y",
        ]:
            os.system("clear")
            remove_progress = ProgressBar(len(corrupted_files))
            for f in corrupted_files:
                remove_progress.increment()
                try:
                    os.remove(f)
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    cprint(f"\n{e}", fg.red, style.bold)
                    continue

        print(f"\nDone: {len(corrupted_files)} successfully removed")
    cprint(f"Done!: {len(corrupted_files)}/{num_media} corrupt...", fg.yellow)


if __name__ == "__main__":
    try:
        args = parse_arguments()
        main(args.path, args.dry_run)
    except KeyboardInterrupt:
        exit(127)
