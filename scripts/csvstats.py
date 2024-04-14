#!/usr/bin/env python3

# avgvalue.py - Calculate the average value of a list of numbers

import argparse
import sys
import os
import re


def parse_args():
    parser = argparse.ArgumentParser(
        description="Calculates the min, max, and mean for each column in a csv file.\n\
            Also works on single column files.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "FILE", 
        help="Enter the file name",
        type=str
        )
    return parser.parse_args()

def main(args):
    try:
        with open(args.FILE) as file:
            header = next(file)
            if ',' in str(header):
                header = header.split(',')

            columns = [str(item) for item in header]
            numbers = file.readlines()
            numbers = [float(x) for x in numbers]
            avg = round(sum(numbers) / len(numbers), 3)
            print(avg)
        sys.exit(0)
    except Exception as e:
        print(e)
        sys.exit(1)

if __name__ == "__main__":
    args = parse_args()
    main(args)