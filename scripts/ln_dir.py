#!/usr/bin/env python3

import os
import subprocess
import re
import glob

import argparse
from MetaData import DirectoryObject, FileObject


def parse_args():
    parser = argparse.ArgumentParser(description = "This script is used as a redneck way to hardlink a directory and its subdirectories", 
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-d", "--directory", help = "The directory to be hardlinked.",
                        default=".")
    parser.add_argument("-p", "--pattern", help="The pattern (PCRE) to match files against.",
                        default = ".*")
    return parser.parse_args()


def main(dir, pattern):
    """ 
    This script is used as a redneck way to hardlink a directory and its subdirectories.
    It recreates the directory tree of the input directory and then hardlinks all files that       match a given pattern in it to the recreated tree.
    """
    path = DirectoryObject(dir)
    
    for folder in dir.rel_directories:
        os.makedirs(folder, exist_ok = True)
        
    for file in dir.rel_files:
        if re.match(pattern, file):
            subprocess.run(['ln', '--hard', f'{dir}/{file}', f'./{file}'])

# Example
if __name__ == "__main__":
    args = parse_args()
    main(args.directory, args.pattern)