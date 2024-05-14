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
        help="Columns to plot",
        nargs="*",
    default=[' cpu_temp', ' system_temp', ' gpu_usage', ' gpu_power', ' gpu_memory_usage']
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
    try:
        # Remove header until we can process it
        df = pd.read_csv(filepath, header=None)
    except FileNotFoundError:
         print(f"File {filepath} not found.")
         return 1
    # Process header and strip whitespace
    for column in columns:
        df[column] = df[column].str.strip()
    

    
    # Remove the 'cpu_max_clock' and 'cpu_avg_clock' columns
    """     
    df_filtered = df.drop(
        [ ' gpu_temp', ' gpu_usage', ' ram_usage',
        ' system_temp', ' ping', ' gpu_power', ' cpu_temp', ' cpu_max_clock', ' cpu_avg_clock'],
        axis=1)

    """

    # df_filtered = df.drop([' cpu_max_clock', ' cpu_avg_clock', ' gpu_temp', ' gpu_power',
    # ' gpu_usage', ' ram_usage', ' system_temp', ' ping'], axis=1),
    df_data = df[columns]
    if any(col not in df_data.columns for col in columns):
        raise ValueError("One or more of the columns do not exist.")

    # Smooth the data using moving averages
    smooth_data = {}
    for column in columns:  # Exclude the 'datetime' column
        smooth_data[column] = np.convolve(
            df_data[column], np.ones(window_size)/window_size, mode='valid')

    # Create a new DataFrame for the smoothed data
    smooth_df = pd.DataFrame(smooth_data)

    # Plot the smooth data
    fig, ax = plt.subplots(figsize=(10, 6))
    line, = ax.plot([], [], label=column)

    def init():
        ax.set_xlim(left=0, right=len(df_data))
        ax.set_ylim(bottom=np.min(smooth_data.values())-1, top=250)
        return line,

    def animate(i):
        new_data = pd.read_csv(filepath)
        ax.clear()
        new_smooth_data = {}
        for column in columns:
            new_smooth_data[column] = np.convolve(
                new_data[column], np.ones(window_size)/window_size, mode='valid')
        new_smooth_df = pd.DataFrame(new_smooth_data)
        new_smooth_df.plot(ax=ax, grid=True)

    ani = FuncAnimation(fig, animate, frames=100, interval=200)  # Update every 1000 milliseconds (1 second)
    plt.show()
    
if __name__ == "__main__":
    args = parse_args()
    main(args.file, args.window, args.COLUMNS)
