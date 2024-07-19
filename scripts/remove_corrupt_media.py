#!/usr/bin/env python3
"""Finds and removes corrupt images and videos."""

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import os

from fsutils import Dir, Img
from ExecutionTimer import ExecutionTimer
from ProgressBar import ProgressBar
from Color import cprint, style, fg


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Finds and removes corrupt images and videos"
    )
    parser.add_argument("path", help="Path to the directory")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Do not remove files, only show what would be done",
    )
    return parser.parse_args()


def process_file(item: Img):
    return (item.is_corrupt, item.path)


def main(path: str, dry_run: bool) -> None:
    with ExecutionTimer():
        corrupted_files = []

        images = Dir(path).images
        num_images = len(images)
        with ProgressBar(num_images) as progress:
            cprint(f"Found {num_images - 1} files", fg.green, style.bold)
            with ThreadPoolExecutor() as executor:
                futures = [executor.submit(process_file, img) for img in images]
                for future in as_completed(futures):
                    try:
                        result = future.result()
                        if result:
                            corrupt, path = result
                            progress.increment()
                            if corrupt:
                                corrupted_files.append(path)  # save for later analysis
                    except Exception as e:
                        cprint(e, fg.red)
                    except KeyboardInterrupt:
                        break
            print("")
            with open("corrupt_files.txt", "w") as f:
                f.write("\n".join(corrupted_files))

            print("\n".join(corrupted_files))

            if not dry_run and corrupted_files:
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


if __name__ == "__main__":
    args = parse_arguments()
    main(args.path, args.dry_run)
