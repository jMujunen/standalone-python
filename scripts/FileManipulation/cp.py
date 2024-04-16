#!/usr/bin/env python3

# cp.py - Copy files from one directory to another

import sys
import os
import argparse
import subprocess
import shutil

from pb import ProgressBar


def parse_args():
    parser = argparse.ArgumentParser(
        description='Move files from one dir to another'
    )
    parser.add_argument(
        'input_dir',
        help='Copy from this directory'
    )
    parser.add_argument(
        'output_dir',
        help='Copy to this directory'
    )
    parser.add_argument(
        '-r',
        '--recursive',
        help='Enable recursive',
        action='store_true',
    )

    return parser.parse_args()

def main(input_dir, output_dir):
    number_of_files = 0
    directory_paths = []
    files_paths = []
    for root, _, filename in os.walk(input_dir):
        directory_paths.append(os.path.join(root, _))
        for file in filename:
            if os.path.isfile(os.path.join(root, file)):
                number_of_files += 1
                file_paths.append(os.path.join(root, file))
    
    progress = ProgressBar(number_of_files)

    for directory in directory_paths:
        if not os.path.exists(directory):
            os.mkdir(directory)

    for file in files_paths:
        if not os.path.exists(file):
            shutil.move()
    for root, _, filename in os.walk(input_dir):
        for file in filename:
            progress.increment()

if __name__ == "__main__":
    args = parse_args()
    main(args.input_dir, args.output_dir)
    print('\n')