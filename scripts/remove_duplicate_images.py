#!/usr/bin/env python3
""" "remove_duplicate_media.py - Finds and removes duplicate images and videos."""

import argparse
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
import imagehash
from pprint import pformat
from collections import OrderedDict

from Color import cprint, fg, style
from ExecutionTimer import ExecutionTimer
from fsutils import Dir, Img
from ProgressBar import ProgressBar

IGNORED_DIRS = [".Trash-1000", "Screenshots"]  # , "RuneLite"]


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
    if any(ignored in item.path for ignored in IGNORED_DIRS):
        return
    if item.is_file and item.is_image:
        h = item.calculate_hash()
        return (h, item.path)
    return


def main(args: argparse.Namespace) -> None:
    with ExecutionTimer():
        hashes = OrderedDict()
        duplicate_files = []
        corrupted_files = []
        directory = Dir(args.path)
        files = len(directory.files) + 1

        cprint(f"Found {files - 1} files", fg.green, style.bold)
        progress = ProgressBar(files)

        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(process_file, file) for file in directory.images]
            for future in as_completed(futures):
                result = future.result()
                if result:
                    progress.increment()
                    hash_value, file = result
                    if hash_value not in hashes:
                        hashes[hash_value] = [file]
                    else:
                        hashes[hash_value].append(file)
        num_dupes = [v for v in hashes.values() if len(v) > 1]
        cprint(f"\nDuplicates found: {len(num_dupes)}", fg.cyan, style.bold)
        for k, v in hashes.items():
            # No hash means file is corrupt, or in otherwords, flag for removal
            if k is None:
                corrupted_files.extend(v)
                # Remove for memory efficiancy
                del hashes[k]
            if len(v) >= 3:
                duplicate_files.append(v)
                if not args.dry_run:
                    # Remove without confirmation prompt
                    if args.no_confirm:
                        for img in v:
                            for i, img in enumerate(v):
                                if i >= 2:
                                    try:
                                        os.remove(img)
                                        cprint(f"{img} removed", fg.green, style.bold)
                                    except FileNotFoundError:
                                        continue
                                else:
                                    cprint(f"Keeping {img}", fg.green)
                    # Render duplicate sets
                    for img in v:
                        print("{:<30} {:<30}".format(" ", img))
                        subprocess.run(
                            f'kitten icat --use-window-size 100,100,500,100 "{img}"',
                            shell=True,
                        )
                    # Prompt for confirmation before removal
                    num_remove = 1
                    reply = input("\033[33mRemove these files? [Y/n]: \033[0m")
                    if reply.lower() == "y" or reply == "" or reply in ["1", "2", "3", "11"]:
                        try:
                            num_remove = len(v) - int(reply) - 1
                        except ValueError:
                            pass
                        for i, img in enumerate(v):
                            # Skip the first 2 or specified value
                            if i > num_remove:
                                try:
                                    os.remove(img)
                                    cprint(f"{img} removed", fg.green, style.bold)
                                except FileNotFoundError:
                                    cprint(f"{img} not found", fg.red, style.bold)
                    else:
                        os.system("clear")

        log_file = os.path.join(os.getcwd(), "common_files.log")
        # content = ",\n".join([f"{i} {v}" for i, v in enumerate(duplicate_files)])
        # content = f"{content}\n\n{"="*60}\n\nCorrupted files:\n{'\n'.join(corrupted_files)}"
        with open(log_file, "w") as f:
            f.write(f"common_files = {pformat(duplicate_files)}")
            f.write(f"\n\n# {'='*60}\n\n# Corrupted files:\n")
            f.write(f"corrupted_files = {pformat(corrupted_files)}")

        cprint(f"Log file saved to {log_file}\n", fg.blue, style.bold)

        print("")


if __name__ == "__main__":
    args = parse_args()
    main(args)
