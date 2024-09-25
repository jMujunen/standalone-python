#!/usr/bin/env python3

# csvgraph.py.py - Generate a graph from a list of numbers

import argparse
import pandas as pd
import re

import matplotlib.pyplot as plt
import numpy as np

DIGITS_RE = re.compile(r"(\d+(\.\d+)?)")
ALL_COLUMNS_KEYWORDS = ["all", "-all", "--all", "-all", "-a", "all_columns"]


def parse_args() -> argparse.Namespace:
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
        help="Moving average value to use for smoothing data. Default is 5.",
    )
    return parser.parse_args()


def main(args) -> None:
    df = pd.read_csv(args.FILE, sep=",", header=None, names=["Timestamp", "Value"])
    smooth_ping = np.convolve(df["Value"], np.ones(args.window) / args.window, mode="valid")
    smooth_df = pd.DataFrame(smooth_ping, columns=["Value"])
    fig, ax = plt.subplots(
        figsize=(16, 6),
        dpi=80,
        edgecolor="#5a93a2",
        linewidth=1,
        tight_layout=True,
        facecolor="#364146",
        subplot_kw={"facecolor": "#2E3539"},
    )

    line = ax.plot([], [], label="Ping")  # use the first column for the label
    plt.title("Ping Graph")
    smooth_df.plot(ax=ax, grid=True, kind="line")
    # plt.legend()
    plt.show()


if __name__ == "__main__":
    args = parse_args()
    main(args)
