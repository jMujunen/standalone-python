#!/usr/bin/env python3

# pandas_plot.py - Plot pandas dataframes

import argparse
import os
import pandas as pd
import sys
from typing import Any

import matplotlib.pyplot as plt
import numpy as np

FILE = "/tmp/hwinfo.csv"

GROUPS = {
    "misc": ["ping", "ram_usage", "core_usage", "gpu_memory_usage"],
    "gpu": ["gpu_core_temp", "gpu_core_usage", "power", "gpu_memory_usage"],
    "temps": [
        "sys_temp",
        "gpu_core_temp",
        "cpu_avg_temp",
        "cpu_max_temp",
    ],
    "cpu": ["cpu_max_clock", "cpu_avg_clock"],
    "volts": ["gpu_voltage", "cpu_voltage"],
    "clocks": ["gpu_core_clock", "gpu_memory_clock", "cpu_max_clock"],
}


def main(filepath: str, columns: list[Any], num_rows: int = -1, smooth_factor: int = 1) -> None:
    """Load CSV file into a dataframe and plot specified columns.

    Parameters
    ----------
        - `smooth_factor` defines moving average or how 'smooth' the line will be.  \
            Default value is a variable calculated based number of rows in the dataframe.
        - `num_rows` defines how many rows to load from the file.
        - `columns` defines which columns to plot.  If column name is not found, it will be ignored \
            as long as there is at least one valid column

    """

    if columns[0] in GROUPS:
        columns = GROUPS[columns[0]]
    if not os.path.isfile(filepath):
        raise FileNotFoundError("File not found.")
    df = pd.read_csv(filepath, sep=r",\s*", engine="python", index_col=0)
    df = df.tail(num_rows)
    missing_columns = [col for col in columns if col not in df.columns]

    # Create index from timestamp
    df.index = pd.to_datetime(df.index)
    df.index = df.index.strftime("%H:%M")

    # Plot the data even if some of the specified columns are missing from the file
    if missing_columns:
        print(
            f"\033[33m[WARNING]\033[0m Columns \033[1;4m{", ".join(missing_columns)}\033[0m do not exist in the file."
        )
        columns = [col for col in columns if col in df.columns] or df.columns  # type: ignore
    print(columns)
    # Smooth the line for easier reading of large datasets
    smooth_data = {}
    if smooth_factor == 1:
        smooth_factor = int(df.shape[0] / 100) or 1
    for column in columns:
        smooth_data[column] = np.convolve(
            df[column], np.ones(smooth_factor) / smooth_factor, mode="valid"
        )

    smooth_df = pd.DataFrame(smooth_data, index=df.index[: -(smooth_factor - 1)])

    fig, ax = plt.subplots(
        figsize=(16, 6),
        dpi=80,
        edgecolor="#5a93a2",
        linewidth=1,
        tight_layout=True,
        facecolor="#364146",
        subplot_kw={"facecolor": "#2E3539"},
    )

    # Y-axis settings
    plt.ylabel("Value", fontsize=14, color="#d3c6aa", fontweight="bold")

    # X-axis settings
    plt.xlabel("")
    ax.set_xlim(left=0, right=len(smooth_df))
    print(len(smooth_df.columns))
    if len(df.columns) == 1:
        smooth_df.plot(
            ax=ax,
            grid=True,
            kind="line",
            color="#a7c080",
        )
    else:
        smooth_df.plot(ax=ax, grid=True, kind="line")

    # plt properties
    plt.grid(True, linestyle="--", alpha=0.3, color="#d3c6a2")
    plt.title(FILE, fontsize=16, color="#d3c6a2", fontweight="bold")
    plt.legend(loc="upper left")

    # plt.yticks(fontsize=12, color="#d3c6aa")
    plt.xticks(rotation=45, fontsize=12, color="#d3c6aa")
    plt.show()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Plot csv data",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        usage="plotcsv.py [OPTIONS] FILE ",
    )
    parser.add_argument(
        "FILE",
        help="Path to the csv file",
        type=str,
        nargs="?",
        default="/tmp/hwinfo.csv",
    )
    parser.add_argument(
        "-s", "--smooth", help="Smoothing factor for the moving average", type=int, default=1
    )
    parser.add_argument(
        "-n", "--num", help="Limit the number of rows to plot", type=int, default=-1
    )
    parser.add_argument("-l", "--list", action="store_true", help="List available columns")
    parser.add_argument(
        "-c",
        "--columns",
        help="""Columns to plot
        Supports groups, such as 'cpu' or 'gpu' or 'temps' .""",
        nargs=argparse.REMAINDER,
        default=["temps"],
    )
    parser.add_argument(
        "--combine", help="Combine several files into one plot", action="store_true"
    )
    # TODO: Add support for limiting the range of the x-axis (time)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if args.list:
        for group in GROUPS:
            print(f"\033[1m{group}\033[0m")
            print(" ", "\n  ".join(GROUPS[group]))
        sys.exit(0)
    main(args.FILE, args.columns, args.num, args.smooth)
