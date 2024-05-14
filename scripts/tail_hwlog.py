#!/usr/bin/env python3

# tail_hwlog.py - Tail the hardware log file in real time

import os, sys, subprocess
import pandas as pd
import argparse


# def parse_args():
#     parser = argparse.ArgumentParser(
#         description="Tail the hardware log file in real time",
#         formatter_class=argparse.ArgumentDefaultsHelpFormatter
#     )
#     parser.add_argument(
#         "FILE", 
#         help="Enter the file name",
#         type=str
#     )
#     parser.add_argument(
#         "-c", "--column",
#         help="Columns to plot",
#         nargs="+",
#         default=["cpu_temp", "gpu_temp", "system_temp", "gpu_usage", "gpu_power"]
#     )
#     return parser.parse_args()



FILE = "/tmp/hwlog.csv"

COLUMNS = [" gpu_temp", " gpu_usage", " gpu_power", " gpu_mem_usage", "gpu_core_clock", "gpu_mem_clock"]

def main(FILE, COLUMNS):
    df = pd.read_csv(FILE)
    df = df[COLUMNS]
    print(df.tail())
    subprocess.call(["clear"])
    main(FILE, COLUMNS)

if __name__ == "__main__":
    main(FILE, COLUMNS)