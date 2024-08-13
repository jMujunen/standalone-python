#!/usr/bin/env python3
""" "remove_duplicate_media.py - Finds and removes duplicate images and videos."""

import argparse
import os
import subprocess
from collections import OrderedDict
from pprint import pformat

import imagehash
from Color import cprint, fg, style
from ExecutionTimer import ExecutionTimer
from fsutils import Dir, Img
from ProgressBar import ProgressBar
from ThreadPoolHelper import Pool

IGNORED_DIRS = [".Trash-1000"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compares hash values of images and removes any duplicates"
    )
    parser.add_argument("path", help="Path to the directory")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only print the duplicate images that would be removed",
    )
    parser.add_argument("--no-confirm", help="Remove without confirmation", action="store_true")
    return parser.parse_args()


def process_file(item: Img) -> tuple[imagehash.ImageHash | None, str] | None:
    """Function for concurrent processing"""
    if any(ignored in item.path for ignored in IGNORED_DIRS):
        return
    if item.is_file and item.is_image:
        h = item.calculate_hash()
        return (h, item.path)
    return


def find_duplicates(path: str) -> OrderedDict:
    hashes = OrderedDict()
    directory = Dir(path)
    files = len(directory.files) + 1

    cprint(f"Found {files - 1} files", fg.green, style.bold)

    pool = Pool()
    for result in pool.execute(process_file, directory.images, progress_bar=True):
        if result is not None:
            image_hash, image_path = result
            if image_hash not in hashes:
                hashes[image_hash] = [image_path]
            else:
                hashes[image_hash].append(image_path)

    return hashes


def process_group(images: list[str]) -> str:
    num_remove = 1
    for img in images:
        print("{:<30} {:<30}".format(" ", img))
        subprocess.run(
            f'kitten icat --use-window-size 100,100,500,100 "{img}"',
            shell=True,
            check=False,
        )
    # Prompt for confirmation before removal
    reply = input("\033[33mRemove these files? [Y/n]: \033[0m")
    if reply.lower() == "y" or reply == "" or reply in ["1", "2", "3", "11"]:
        try:
            num_remove = len(images) - int(reply) - 1
        except ValueError:
            pass
        for i, img in enumerate(images):
            # Skip the first 2 or specified value
            if i > num_remove:
                try:
                    os.remove(img)
                    cprint(f"{img} removed", fg.green, style.bold)
                except FileNotFoundError:
                    cprint(f"{img} not found", fg.red, style.bold)


def remove_duplicates(hashes: OrderedDict) -> None:
    corrupted_files = []
    duplicate_files = []

    for k, v in hashes.items():
        # No hash means file is corrupt, or in otherwords, flag for removal
        if k is None:
            corrupted_files.extend(v)
            # Remove for memory efficiancy
            del hashes[k]
        if len(v) >= 3:
            duplicate_files.append(v)
            if not args.dry_run and args.no_confirm:
                # Remove without confirmation prompt
                for i, _img in enumerate(v):
                    if i < 2:  # Skip the first two files
                        continue
                    try:
                        os.remove(_img)
                        cprint(f"{_img} removed", fg.green, style.bold)
                    except FileNotFoundError:
                        continue
                    except Exception as e:
                        cprint(f"Error (line{}) removing file: {_img}\n{e}", fg.red, style.bold)

                else:
                    os.system("clear")


def main(args: argparse.Namespace) -> None:
    with ExecutionTimer():
        hashes = find_duplicates(args.path)
        num_dupes = [v for v in hashes.values() if len(v) > 1]
        cprint(f"\nDuplicates found: {len(num_dupes)}", fg.cyan, style.bold)

        log_file = os.path.join(os.getcwd(), "common_files.log")
        # content = ",\n".join([f"{i} {v}" for i, v in enumerate(duplicate_files)])
        # content = f"{content}\n\n{"="*60}\n\nCorrupted files:\n{'\n'.join(corrupted_files)}"
        with open(log_file, "w") as f:
            f.write(f"common_files = {pformat(num_dupes)}")

        cprint(f"Log file saved to {log_file}\n", fg.blue, style.bold, end="\n\n")


if __name__ == "__main__":
    args = parse_args()
    main(args)
