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
    return parser.parse_args()


def main(args):
    with open(args.FILE) as f:
        content = f.readlines()
    parsed_data = [(line.strip().split(",")[0], line.strip().split(",")[1]) for line in content]
    df = pd.DataFrame(parsed_data, columns=["Timestamp", "Value"])

    plt.figure(figsize=(20, 6))
    plt.plot(df["Timestamp"], df["Value"])
    plt.legend()

    plt.title("Ping Graph")
    plt.xlabel("Timestamp")
    plt.ylabel("Value")
    plt.show()


if __name__ == "__main__":
    args = parse_args()
    main(args)
