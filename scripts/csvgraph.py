#!/usr/bin/env python3

# gcsv.py - Generate a graph from a list of numbers


import sys
import argparse
import re

import matplotlib.pyplot as plt

DIGITS_RE = re.compile(r"(\d+(\.\d+)?)")
ALL_COLUMNS_KEYWORDS = [
    "all",
    "-all",
    "--all",
    "-all",
    "-a",
    "all_columns",
]


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate a graph from numbers in a file.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("FILE", help="Enter the file name", type=str)
    parser.add_argument(
        "-c",
        "--column",
        help='''If input is a csv file, choose which column to graph.
        Valid values are str(header) or int(header)
            Examples:
                - graph.py /tmp/cpu_data.csv -c 1
                - graph.py /tmp/cpu_data.csv -c "average_clock"''',
        nargs="+",
    )

    return parser.parse_args()


def main(args: argparse.Namespace) -> None:
    try:
        with open(args.FILE) as file:
            header = next(file)
            """
            TODO: Add support for column range including all
            for column in args.column:
                # Processes all columns if `all|-all|--all` ...  is passed
               if column in ALL_COLUMNS_KEYWORDS:
            """
            if args.column:
                for column in args.column:
                    try:
                        column = int(column)
                        numbers = file.readlines()
                        numbers = [(x.split(",")[column]) for x in numbers]
                        numbers = [
                            DIGITS_RE.findall(numbers[x]) for x in range(len(numbers))
                        ]
                        numbers = [float(x[0][0]) for x in numbers]
                        plt.plot(numbers)
                        plt.show()
                    except Exception:
                        try:
                            args.column = str(column)
                        except Exception:
                            print("Invalid column type")
                            return
                        h = header.split(", ")
                        column = h.index(column)
                        numbers = file.readlines()
                        numbers = [float(x.split(",")[column]) for x in numbers]
                        numbers = [
                            DIGITS_RE.findall(str(numbers[x]))
                            for x in range(len(numbers))
                        ]
                        numbers = [float(x[0][0]) for x in numbers]
                        plt.plot(numbers)
                        plt.show()
                print("Invalid column type")
                sys.exit(1)
            else:
                numbers = file.readlines()
                numbers = [float(x) for x in numbers[1:] if len(x) < 20]
                plt.plot(numbers)
                plt.show()
        sys.exit(0)
    except KeyboardInterrupt:
        sys.exit(1)


# Example
if __name__ == "__main__":
    args = parse_args()
    main(args)
