#!/usr/bin/env python3

# graph.py - Generate a graph from a list of numbers

import os
import sys
import argparse
import re

import matplotlib.pyplot as plt

DIGITS_RE = re.compile(r'(\d+(\.\d+)?)')

def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate a graph from numbers in a file.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "FILE", 
        help="Enter the file name",
        type=str
        )
    parser.add_argument(
        "-c", "--column",
        help='''If input is a csv file, choose which column to graph.
        Valid values are str(header) or int(header)
            Examples: 
                - graph.py /tmp/cpu_data.csv -c 1
                - graph.py /tmp/cpu_data.csv -c "average_clock"''',
    )
    return parser.parse_args()

def main(args):
    try:
        with open(args.FILE) as file:
            if args.column:
                try:
                    args.column = int(args.column)
                    numbers = file.readlines()
                    numbers = [(x.split(',')[args.column]) for x in numbers]
                    numbers = [DIGITS_RE.findall(numbers[x]) for x in range(len(numbers))]
                    numbers = [float(x[0][0]) for x in numbers]
                    plt.plot(numbers)
                    plt.show()

                except Exception as e:
                    try:
                        args.column = str(args.column)
                    except Exception as e:
                        print('Invalid column type')
                        sys.exit(1)
                    header = next(file).split(',')
                    args.column = header.index(args.column)
                    numbers = file.readlines()
                    numbers = [(x.split(',')[args.column]) for x in numbers]
                    numbers = [DIGITS_RE.findall(numbers[x]) for x in range(len(numbers))]
                    numbers = [float(x[0][0]) for x in numbers]
                    plt.plot(numbers)
                    plt.show()
                else:
                    print('Invalid column type')
                    sys.exit(1)
            else:
                numbers = file.readlines()
                numbers = [float(x) for x in numbers]
                plt.plot(numbers)
                plt.show()
        sys.exit(0)
    except Exception as e:
        print(e)
        sys.exit(1)


# Example
if __name__ == "__main__":
    args = parse_args()
    main(args)