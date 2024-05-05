#!/usr/bin/env python3

# pandas_plot.py - Plot pandas dataframes

import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

FILE = "/tmp/hwinfo.csv"

def main():
    df = pd.read_csv(FILE)

    # Remove the 'cpu_max_clock' and 'cpu_avg_clock' columns
    df_filtered = df.drop(
        [ ' gpu_temp', ' gpu_usage', ' ram_usage',
        ' system_temp', ' ping', ' gpu_power', ' cpu_temp', ' cpu_max_clock', ' cpu_avg_clock'],
        axis=1)
    #df_filtered = df.drop([' cpu_max_clock', ' cpu_avg_clock', ' gpu_temp', ' gpu_power', 
    #' gpu_usage', ' ram_usage', ' system_temp', ' ping'], axis=1), 

    # Smooth the data using moving averages
    window_size = 100  # You can adjust the window size as needed
    smoothed_data = {}
    for column in df_filtered.columns[1:]:  # Exclude the 'datetime' column
        smoothed_data[column] = np.convolve(df_filtered[column], np.ones(window_size)/window_size, mode='valid')

    # Create a new DataFrame for the smoothed data
    smoothed_df = pd.DataFrame(smoothed_data)

    # Plot the smoothed data
    smoothed_df.plot(figsize=(10, 6), grid=True)
    plt.show()

def animate(i):
    new_data = df = pd.read_csv(FILE)
    # Update the plot with the new data
    ax.clear()
    ax.plot(new_data)  # Plot the new data



if __name__ == "__main__":
    main()