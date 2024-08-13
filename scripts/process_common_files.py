#!/usr/bin/env python3

import os
import subprocess
import sys

from Color import cprint, fg, style
from ProgressBar import ProgressBar

from parse_list_from_file import find_lists


def main(file: str) -> None:
    """Processes a file containing image lists and allows the user to delete them.

    Parameters:
    ------------
        - `file (str)` : The path to the file containing image lists.
            Each list represents a group of images, and each line in a list is an image path.
    """
    with open(file) as f:
        content = f.read()

    common_files = find_lists(content)

    for item in common_files:
        cprint(f"{"=" * 20}| {item[-1]} |{"=" * 20}", style.bold)
        for img in item:
            subprocess.run(
                f'kitten icat --use-window-size 100,100,500,100 "{img}"',
                shell=True,
                check=False,
            )
    reply = input("\nDo you want to delete these files? (y/N): ")
    if reply.lower() == "y":
        while True:
            try:
                num_remove = int(input("\nHow many to remove: "))
                break
            except ValueError:
                print("Input an integer\n")
                continue
        with ProgressBar(len(common_files)) as progress:
            for item in common_files:
                progress.increment()
                for i, img in enumerate(item):
                    if len(item) > 1 and i > len(item) - int(num_remove) - 1:
                        os.remove(img)
                        cprint(f"Successfully removed {img}")
                    else:
                        continue

        cprint("\nFiles removed successfully", style.bold, fg.green)

    elif reply.lower() != "n":
        print("Invalid input")
        return None


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: process_common_files.py <common_files.log>")
        exit()
    main(sys.argv[1])
