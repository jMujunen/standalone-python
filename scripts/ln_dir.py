#!/usr/bin/env python3

import os
import subprocess
import re
import glob

import argparse
from MetaData import Dir, File


def parse_args():
    parser = argparse.ArgumentParser(description="This script is used as a redneck way to hardlink a directory and its subdirectories", 
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("dir", help="The directory to be hardlinked.",
                        default=".")
    parser.add_argument('-o', '--output', help='path to the link: Default: pwd', required=False, default=os.getcwd())
    parser.add_argument("-p", "--pattern", help="The pattern (PCRE) to match files against.",
                        default = ".*")
    return parser.parse_args()


def mklinks(src, dst, pattern):
    for file in os.listdir(src):
        if os.path.isfile(os.path.join(src, file)) and re.match(pattern, file):
            link = os.path.join(dst, file)
            print("Linking {} to {}".format(link, os.path.join(src, file)))
            try: 
                os.link(os.path.join(src, file), link)
            except FileExistsError as e:
                print('File already exists')
        elif os.path.isdir(os.path.join(src, file)):
            mklinks(os.path.join(src, file), os.path.join(dst, file), pattern)

def main(input_path, output_path, pattern):
    """ 
    This script is used as a redneck way to hardlink a directory and its subdirectories.
    It recreates the directory tree of the input directory and then hardlinks all files that       match a given pattern in it to the recreated tree.
    """
    dir = Dir(input_path)
    if not os.path.exists(output_path):
        # Create parents
        os.makedirs(output_path)
    try:
        mklinks(input_path, output_path, pattern)
    except:
        pass
    for folder in dir.rel_directories:
        try:
            new_folder = os.path.abspath(os.path.join(output_path, folder))
            os.makedirs(new_folder, exist_ok=True)
            mklinks(os.path.join(input_path, folder), new_folder, pattern)
            folder = Dir(new_folder)
        except Exception as e:
            print("Error while processing directory", folder, ":", str(e))
# Example
if __name__ == "__main__":
    args = parse_args()
    main(args.dir, args.output, args.pattern)