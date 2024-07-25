#!/usr/bin/env python3

# remove_installation_files.py - Generates a list of files / directories
# to be removed based on the output of 'sudo pacman -U'

import argparse
import subprocess
import os
import re
import sys


def parse_args():
    parser = argparse.ArgumentParser(
        description=("Remove files / directories listed when `sudo pacman -U` fails")
    )
    parser.add_argument("PROGRAM_NAME", help="Program to remove")

    return parser.parse_args()


def main(program_name):
    basename = program_name.split("-")[0]
    print(basename)
    path_regex = re.compile(rf"{basename}.*:\s(.*)\sexists")
    output = subprocess.run(
        f"sudo pacman -U --noconfirm --noprogressbar {program_name}",
        shell=True,
        capture_output=True,
        text=True, check=False,
    ).stderr.strip()

    matches = re.findall(path_regex, output)
    count = 0
    for match in matches:
        count += 1
        print(match)
    confirm = input(f"Are you sure you want to remove {count} files? [y/N]: ")
    if not confirm or confirm.strip().lower() != "y":
        sys.exit(1)
    else:
        for match in matches:
            try:
                os.remove(match)
            except Exception as e:
                print(f"Error: {e}")
                continue
    if matches:
        print(f"Removed {count} files")
    else:
        print("Error: Are you in the correct directory?")


# Example
if __name__ == "__main__":
    args = parse_args()
    main(args.PROGRAM_NAME)
