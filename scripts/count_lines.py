#!/usr/bin/env python3 

# count_lines.py - Count the number of lines in a given file

import argparse



def parse_args():
    parser = argparse.ArgumentParser(
        description="Count the number of lines in a given file."
    )
    parser.add_argument("file", help="Enter the file name")
    return parser.parse_args()


def main(args):
    with open(args.file, "r") as f:
        num_lines = int(len(f.readlines()))
    return num_lines


if __name__ == "__main__":
    args = parse_args()
    print(main(args))
    