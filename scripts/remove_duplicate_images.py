#!/usr/bin/env python3
""" "remove_duplicate_media.py - Finds and removes duplicate images and videos."""

import argparse
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor
from Color import cprint, fg, style
from ExecutionTimer import ExecutionTimer
from fsutils.DirNode import Dir, Img
from ProgressBar import ProgressBar

IGNORED_DIRS = [".Trash-1000", "Screenshots", "RuneLite"]


def parse_args():
    parser = argparse.ArgumentParser(
        description="Compares hash values of images and removes any duplicates"
    )
    parser.add_argument("path", help="Path to the directory")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only print the duplicate images that would be removed",
    )
    return parser.parse_args()


def process_file(item: Img):
    if any(ignored in item.path for ignored in IGNORED_DIRS):
        return None
    if item.is_file and item.is_image:
        hash = item.calculate_hash()
        return (hash, item.path)
    return None


def main(args):
    with ExecutionTimer():
        hashes = {}
        duplicate_files = []
        corrupted_files = []
        directory = Dir(args.path)
        files = len(directory.files) + 1

        cprint(f"Found {files - 1} files", fg.green, style.bold)
        progress = ProgressBar(files)

        with ThreadPoolExecutor() as executor:
            futures = {executor.submit(process_file, file): file for file in directory}
            for future in futures:
                result = future.result()
                if result:
                    progress.increment()
                    hash, file = result
                    if hash not in hashes:
                        hashes[hash] = [file]
                    else:
                        hashes[hash].append(file)

        for k, v in hashes.items():
            # No hash means file is corrupt, or in otherwords, flag for removal
            if k is None:
                corrupted_files.extend(v)
                continue
            if len(v) > 1:
                duplicate_files.append(v)
                if not args.dry_run:
                    for img in v:
                        subprocess.run(
                            f'kitten icat --use-window-size 500,100,500,100 "{img}"',
                            shell=True,
                        )

                    reply = input("\033[33mRemove these files? [Y/n]: \033[0m")
                    if reply.lower() == "y" or reply == "":
                        for i, img in enumerate(v):
                            # Skip the first image
                            if i == 0:
                                continue
                            try:
                                os.remove(img)
                                cprint(f"{img} removed", fg.green, style.bold)
                            except FileNotFoundError:
                                cprint(f"{img} not found", fg.red, style.bold)
                                next
                    else:
                        os.system("clear")
                        continue

        log_file = os.path.join(os.getcwd(), "common_files.log")
        content = ",\n".join([f"{i} {v}" for i, v in enumerate(duplicate_files)])
        content = f"{content}\n\n{"="*60}\n\nCorrupted files:\n{'\n'.join(corrupted_files)}"
        with open(log_file, "w") as f:
            f.write(content)

        cprint(f"\nLog file saved to {log_file}\n", fg.blue, style.bold)
        subprocess.run(
            ["kitten", "say", "-v", "Fred", f'"Duplicate files have been logged to {log_file}"']
        )

        print("")


if __name__ == "__main__":
    args = parse_args()
    main(args)
