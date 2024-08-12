#!/usr/bin/env python3

# gcsv.py - Generate a graph from a list of numbers


import argparse
import pandas as pd
import re
import sys

import matplotlib.pyplot as plt

DIGITS_RE = re.compile(r"(\d+(\.\d+)?)")
ALL_COLUMNS_KEYWORDS = ["all", "-all", "--all", "-all", "-a", "all_columns"]


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate a graph from numbers in a file.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "FILE",
        help="Enter the file name",
        nargs="?",
        default="/tmp/hwinfo.csv",
    )
    parser.add_argument(
        "-c",
        "--column",
        help='''If input is a csv file, choose which column to graph.
        Valid values are str(header) or int(header)
            Examples:
                - graph.py /tmp/cpu_data.csv -c 1
                - graph.py /tmp/cpu_data.csv -c "average_clock"''',
        nargs="+",
        default="all",
    )

    return parser.parse_args()


def main(args):
    try:
        df = pd.read_csv(args.FILE)

        if args.column in ALL_COLUMNS_KEYWORDS or not args.column:
            columns = [DIGITS_RE.findall(str(df[col])) for col in df.columns]
            valid_columns = [[float(x[0][0]) for x in cols if len(x) == 1] for cols in columns]
            valid_columns = [col for col in valid_columns if len(col) > 0]

            if not valid_columns:
                print("Error: No valid number columns found.")
                sys.exit(1)

            plt.figure(figsize=(8, 6))
            for i, col in enumerate(valid_columns):
                plt.plot(*col, label=df.columns[i], drawstyle="steps-mid")
            if len(valid_columns) > 1:
                plt.legend()
        else:
            numbers = df.iloc[:, int(args.column)]
            plt.figure(figsize=(8, 6))
            plt.plot(numbers, drawstyle="steps-mid")

        plt.title("Graph from file")
        plt.xlabel("Index")
        plt.ylabel("Value")
        plt.show()
    except KeyboardInterrupt:
        print("\nOperation interrupted by user.")
        sys.exit(127)


if __name__ == "__main__":
    args = parse_args()
    main(args)
