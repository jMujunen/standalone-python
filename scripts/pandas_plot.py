#!/usr/bin/env python3

# pandas_plot.py - Plot pandas dataframes

import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import argparse

FILE = "/tmp/hwinfo.csv"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Plot pandas dataframes",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "-f", "--file",
        help="Path to the csv file",
        type=str
    )
    parser.add_argument(
        "-w", "--window",
        help="Window size for the moving average",
        type=int
    )
    parser.add_argument(
        "COLUMNS",
        help="Columns to plot",
        nargs="*",
        default=['cpu_temp', 'gpu_temp', 'system_temp', 'ping']
    )
    return parser.parse_args()


def main(filepath, window_size=100, columns=3):
    df = pd.read_csv(filepath)

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
    # Smooth the data using moving averages
    smoothed_data = {}
    for column in columns:  # Exclude the 'datetime' column
        smoothed_data[column] = np.convolve(
            df_filtered[column], np.ones(window_size)/window_size, mode='valid')

    # Create a new DataFrame for the smoothed data
    smoothed_df = pd.DataFrame(smoothed_data)

    # Plot the smoothed data
    smoothed_df.plot(figsize=(10, 6), grid=True)
    plt.show()


def animate(i):
    new_data = df = pd.read_csv(filepath)
    # Update the plot with the new data
    ax.clear()
    ax.plot(new_data)  # Plot the new data


if __name__ == "__main__":
    args = parse_args()
    main(args.file, args.window, args.COLUMNS)
