#!/usr/bin/env python3
""" "remove_duplicate_media.py - Finds and removes duplicate images and videos."""

import argparse
import os
import subprocess
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pprint import pformat

import imagehash
from Color import cprint, fg, style
from ExecutionTimer import ExecutionTimer
from fsutils import Dir, Img
from ProgressBar import ProgressBar

IGNORED_DIRS = [".Trash-1000"]


def parse_args() -> argparse.Namespace:
    """Argument parsing"""
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


def process_file(item: Img) -> tuple[imagehash.ImageHash | None, Img] | None:
    """Function for concurrent processing"""
    if any(ignored in item.path for ignored in IGNORED_DIRS):
        return
    if item.is_file and item.is_image:
        h = item.calculate_hash()
        return (h, item)
    return


def dry_run():
    return 0


def find_duplicates() -> OrderedDict[imagehash.ImageHash | None, Img]:
    """Finds duplicate images"""
    hashes = OrderedDict()
    images = Dir(args.path).images
    nun_images = len(images)

    cprint(f"Found {nun_images - 1} files", fg.green, style.bold)
    progress = ProgressBar(nun_images)

    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_file, img) for img in images]
        for future in as_completed(futures):
            result = future.result()
            if result:
                progress.increment()
                hash_value, img_object = result
                if hash_value not in hashes:
                    hashes[hash_value] = [img_object]
                else:
                    hashes[hash_value].append(img_object)

    return hashes


def remove_duplicates(hashes: OrderedDict, dryrun=False):
    corrupted_files = []
    duplicate_files = []
    num_keep = 2
    for k, v in hashes.items():
        # No hash means file is corrupt, or in otherwords, flag for removal
        if k is None or k.is_corrupt:
            corrupted_files.extend(v)
            # Remove for memory efficiancy
            del hashes[k]
        elif len(v) >= 3:
            duplicate_files.append(v)

    if dryrun:
        return dry_run()

    for group in duplicate_files:
        if not args.no_confirm:
            cprint("Duplicate files:", style.bold)
            for idx, img in enumerate(group):
                print("{:<30} {:<30}".format(" ", img.basename))
                img.render()
            reply = input("Remove these files? [Y/n]: ")
            if reply.lower() == "y" or reply == "" or reply in ["1", "2", "3", "11"]:
                try:
                    num_keep = len(group) - int(reply) - 1
                except ValueError:
                    pass

                for i, img in enumerate(group):
                    if i > num_keep:
                        try:
                            os.remove(img.path)
                            cprint(f"{img.path} removed", fg.green)
                        except FileNotFoundError:
                            cprint(f"Error removing {img.path}: File does not exist.", fg.red)
            else:
                os.system("clear")
        else:
            for img in group[2:]:  # Remove all but the first two duplicates in group by default
                try:
                    os.remove(img.path)
                    cprint(f"{img.path} removed", fg.green)
                except FileNotFoundError:
                    continue

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


def main(args: argparse.Namespace) -> None:
    with ExecutionTimer():
        hashes = find_duplicates()
        num_dupes = [v for v in hashes.values() if len(v) > 1]
        cprint(f"\nDuplicates found: {len(num_dupes)}", fg.cyan, style.bold)

        log_file = os.path.join(os.getcwd(), "common_files.log")
        # content = ",\n".join([f"{i} {v}" for i, v in enumerate(duplicate_files)])
        # content = f"{content}\n\n{"="*60}\n\nCorrupted files:\n{'\n'.join(corrupted_files)}"
        with open(log_file, "w") as f:
            f.write(f"common_files = {pformat(num_dupes)}")
            f.write(f"\n\n# {'='*60}\n\n# Corrupted files:\n")

        cprint(f"Log file saved to {log_file}\n", fg.blue, style.bold)

        print("")


if __name__ == "__main__":
    args = parse_args()
    main(args)
