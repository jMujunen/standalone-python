#!/usr/bin/env python3

import os
import subprocess
import re
import argparse

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


# Example
if __name__ == "__main__":
    args = parse_args()
    main(args.directory, args.pattern)