#!/usr/bin/env python3

# avgvalue.py - Calculate the average value of a list of numbers


import sys
import csv
from statistics import mean
from ExecutionTimer import ExecutionTimer

FILE = "/tmp/hwinfo.csv"


def main(csv_file):
    with open(csv_file, "r") as f:
        reader = csv.reader(f)
        header = next(reader)

        if len(header) == 1:  # Single column file
            numbers = [float(row[0]) for row in reader]
            avg = round(mean(numbers), 3)
            print(avg)
            sys.exit(0)

        else:  # Multiple columns
            data = list(zip(*reader))  # Transpose the data so we can access by column

    for i, col in enumerate(header):
        if i == 0:
            # Skip datetime col
            continue
        try:
            numbers = [float(x) for x in data[i] if "Network is unreachable" not in x]
            min_value = round(min(numbers), 3)
            max_value = round(max(numbers), 3)
            mean_value = round(mean(numbers), 3)

            print(
                f"\x1b[1m{col.strip()}:\x1b[0m\n min: {min_value}\n max: {max_value}\n mean: {mean_value}",
                end="\n\n",
            )
        except (IndexError, ValueError) as e:
            print("Error processing column", col, ": ", str(e), sep="")

        # TODO : Pretty print output
    return


if __name__ == "__main__":
    with ExecutionTimer():
        if len(sys.argv) > 1:
            FILE = sys.argv[1]  # Use the file given as argument, if any
        main(FILE)
