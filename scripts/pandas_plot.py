#!/usr/bin/env python3

# pandas_plot.py - Plot pandas dataframes

import argparse
import os
import pandas as pd
from typing import List

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation

FILE = "/tmp/hwinfo.csv"

GROUPS = {
    "misc": [" ping", " ram_usage", " gpu_core_usage"],
    "gpu": [" gpu_temp", " gpu_core_usage", " gpu_power"],
    "temps": [" system_temp", " gpu_temp", " cpu_temp"],
    "cpu_clocks": [" cpu_max_clock", " cpu_avg_clock"],
    "volts": [" gpu_volage", " cpu_voltage"],
}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Plot pandas dataframes",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-f", "--file", help="Path to the csv file", type=str, default="/tmp/hwinfo.csv"
    )
    parser.add_argument(
        "-w",
        "--window",
        help="Window size for the moving average",
        type=int,
        default=100,
    )
    parser.add_argument(
        "COLUMNS",
        help="""Columns to plot
        Supports groups, such as 'cpu' or 'gpu' or 'temps' .""",
        nargs="*",
        default=["temps"],  # , 'system_temp', 'gpu_usage', 'gpu_power', 'gpu_memory_usage']
    )
    # TODO: Add support for limiting the range of the x-axis (time)
    return parser.parse_args()


def main(filepath: str, window_size: int, columns: list[str]) -> None:
    """Main entry point for the program."""
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"File {filepath} not found.")
    df = pd.read_csv(filepath, sep=r",")
    missing_columns = [col for col in columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Columns {", ".join(missing_columns)} do not exist in the file.")

    if any(col not in df.columns for col in columns):
        raise ValueError("One or more of the columns do not exist.")

    # smooth_data = {}
    # for column in columns:
    #     smooth_data[column] = np.convolve(
    #         df[column], np.ones(window_size) / window_size, mode="valid"
    #     )
    smooth_data = {}
    for column in columns:
        smooth_data[column] = np.convolve(
            df[column], np.ones(window_size) / window_size, mode="valid"
        )
    smooth_df = pd.DataFrame(smooth_data)

    fig, ax = plt.subplots(figsize=(10, 6))
    line = ax.plot([], [], label=columns[0])  # Changed to use the first column for the label

    def init():
        ax.set_xlim(left=0, right=len(df))
        ax.set_ylim(
            bottom=np.min(smooth_df.values) - 1, top=250
        )  # Used smooth_df instead of smooth_data
        return line

    def animate(i):
        new_data = pd.read_csv(filepath, sep=",", engine="python")
        new_smooth_data = {}
        for column in columns:
            new_smooth_data[column] = np.convolve(
                new_data[column], np.ones(window_size) / window_size, mode="valid"
            )
        new_smooth_df = pd.DataFrame(new_smooth_data)
        ax.clear()
        new_smooth_df.plot(ax=ax, grid=True)

    # ani = FuncAnimation(fig, animate, frames=100, interval=200)
    FuncAnimation(
        fig, animate, frames=100, interval=200
    )  # Update every 1000 milliseconds (1 second)
    plt.show()


if __name__ == "__main__":
    args = parse_args()
    if args.COLUMNS[0] in GROUPS.keys():
        args.COLUMNS = GROUPS[args.COLUMNS[0]]
    main(args.file, args.window, args.COLUMNS)
