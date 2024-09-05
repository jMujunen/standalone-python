#!/usr/bin/env python3

# pandas_plot.py - Plot pandas dataframes

import argparse
import os
import pandas as pd

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation

FILE = "/tmp/hwinfo.csv"

GROUPS = {
    "misc": [" ping", " ram_usage", " gpu_core_usage"],
    "gpu": [" gpu_temp", " gpu_core_usage", " gpu_power"],
    "temps": [" system_temp", " gpu_temp", " cpu_temp"],
    "cpu": [" cpu_max_clock", " cpu_avg_clock"],
    "volts": [" gpu_volage", " cpu_voltage"],
}


def main(filepath: str, window_size: int, columns: list[str]) -> None:
    """Load CSV file into a dataframe and plot specified columns

    ### Notes:
        - `window_size` defines moving average or how 'smooth' the line will be.

    """
    if columns[0] in GROUPS:
        columns = GROUPS[args.COLUMNS[0]]

    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"File {filepath} not found.")
    df = pd.read_csv(filepath, sep=r",")
    missing_columns = [col for col in columns if col not in df.columns]

    if missing_columns:
        raise ValueError(f"Columns {", ".join(missing_columns)} do not exist in the file.")

    # Replace the non-numeric values with NaNs and convert floats
    smooth_data = {}
    for column in columns:
        smooth_data[column] = np.convolve(
            df[column], np.ones(window_size) / window_size, mode="valid"
        )
    smooth_df = pd.DataFrame(smooth_data)

    fig, ax = plt.subplots(figsize=(16, 6))
    line = ax.plot([], [], label=columns[0])  # use the first column for the label
    (line,) = ax.plot([], [], label=columns[0])

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
        # Set x-axis ticks and labels
        num_ticks = 12
        plt.xlabel("Time")
        plt.ylabel("Value")
        tick_interval = len(new_smooth_df) / num_ticks
        ax.set_xticks(np.arange(0, len(new_smooth_df), tick_interval))

        # Formatting timestamps if your data has a datetime index or column
        if isinstance(new_smooth_df.index, pd.DatetimeIndex):
            labels = new_smooth_df.index[
                :: int(tick_interval)
            ]  # Use integer indexing to match the tick interval
            ax.set_xticklabels(
                labels, rotation=45
            )  # Rotate labels for better readability if needed
        else:
            pass
        new_smooth_df.plot(ax=ax, grid=True)

    ani = FuncAnimation(fig, animate, frames=100, interval=200)  # type: ignore
    plt.xlabel("Time")
    plt.show()


def parse_args():
    parser = argparse.ArgumentParser(
        description="Plot pandas dataframes",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-f", "--file", help="Path to the csv file", type=str, default="/tmp/hwinfo.csv"
    )
    parser.add_argument(
        "-w", "--window", help="Window size for the moving average", type=int, default=100
    )
    parser.add_argument("-l", "--list", action="store_true", help="List available columns")
    parser.add_argument(
        "COLUMNS",
        help="""Columns to plot
        Supports groups, such as 'cpu' or 'gpu' or 'temps' .""",
        nargs="*",
        default=["temps"],
    )
    # TODO: Add support for limiting the range of the x-axis (time)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if args.list:
        for group in GROUPS:
            print(f"\033[1m{group}\033[0m")
            print(" ", "\n  ".join(GROUPS[group]))
        exit(0)
    main(args.file, args.window, args.COLUMNS)
