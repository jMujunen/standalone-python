#!/usr/bin/env python3

# gcsv.py - Generate a graph from a list of numbers


import argparse
import pandas as pd
import re

import matplotlib.pyplot as plt
import numpy as np

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
        default="/home/joona/Logs/Network/tmp2.csv",
    )
    parser.add_argument(
        "-w",
        "--window",
        type=int,
        default=5,
        help="The size of the window to use for smoothing data. Default is 5.",
    )
    return parser.parse_args()


def main(args) -> None:
    df = pd.read_csv(args.FILE, sep=",", header=None, names=["Timestamp", "Value"])
    df["Value"] = np.convolve(df["Value"], np.ones(args.window) / args.window, mode="valid")
    fig, ax = plt.subplots(figsize=(16, 6))
    line = ax.plot([], [], label="Ping")  # use the first column for the label
    (line,) = ax.plot([], [], label="Ping")
    plt.title("Ping Graph")
    df.plot(ax=ax, grid=True, kind="line", x="Timestamp", y="Value")
    # plt.legend()
    plt.show()


if __name__ == "__main__":
    args = parse_args()
    main(args)
