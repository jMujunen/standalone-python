#!/usr/bin/env python3

# pandas_plot.py - Plot pandas dataframes

import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import argparse
from matplotlib.animation import FuncAnimation

FILE = "/tmp/hwinfo.csv"
GROUPS = {
    "misc": ["ping", "ram_usage"],
    "gpu": ["gpu_temp", "gpu_usage", "gpu_power"],
    "temps": ["system_temp", "gpu_temp", "cpu_temp"],
    
}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Plot pandas dataframes",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "-f", "--file",
        help="Path to the csv file",
        type=str,
        default="/tmp/hwinfo.csv"
    )
    parser.add_argument(
        "-w", "--window",
        help="Window size for the moving average",
        type=int,
        default=100
    )
    parser.add_argument(
        "COLUMNS",
        help="""Columns to plot
        Supports groups, such as 'cpu' or 'gpu' or 'temps' .""",
        nargs="*",
    default=['cpu_temp'] #, 'system_temp', 'gpu_usage', 'gpu_power', 'gpu_memory_usage']
    )
    return parser.parse_args()


def main(filepath, window_size, columns):
    """Main entry point for the program.

    Args:
        filepath (str): Path to the csv file to plot.
        window_size (int, optional): Window size for the moving average. Defaults to 100.
        columns (list, optional): Columns to plot. Defaults to ['cpu_temp', 'gpu_temp', 'system_temp', 'ping'].

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If any of the columns do not exist.

    Returns:
        None
    """
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"File {filepath} not found.")
    df = pd.read_csv(filepath, sep=r',\s+')
    if any(col not in df.columns for col in columns):
        raise ValueError("One or more of the columns do not exist.")

    smooth_data = {}
    for column in columns:
        smooth_data[column] = np.convolve(
            df[column], np.ones(window_size)/window_size, mode='valid')

    smooth_df = pd.DataFrame(smooth_data)

    fig, ax = plt.subplots(figsize=(10, 6))
    line, = ax.plot([], [], label=columns[0])  # Changed to use the first column for the label

    def init():
        ax.set_xlim(left=0, right=len(df))
        ax.set_ylim(bottom=np.min(smooth_df.values)-1, top=250)  # Used smooth_df instead of smooth_data
        return line,

    def animate(i):
        new_data = pd.read_csv(filepath, sep=r',\s+', engine='python')
        new_smooth_data = {}
        for column in columns:
            new_smooth_data[column] = np.convolve(
                new_data[column], np.ones(window_size)/window_size, mode='valid')
        new_smooth_df = pd.DataFrame(new_smooth_data)
        ax.clear()
        new_smooth_df.plot(ax=ax, grid=True)

    ani = FuncAnimation(fig, animate, frames=100, interval=200)
    ani = FuncAnimation(fig, animate, frames=100, interval=200)  # Update every 1000 milliseconds (1 second)
    plt.show()
    
if __name__ == "__main__":
    args = parse_args()
    if args.COLUMNS[0] in GROUPS.keys():
        args.COLUMNS = GROUPS[args.COLUMNS[0]]
    main(args.file, args.window, args.COLUMNS)
