#!/usr/bin/env python3
"""avgvalue.py - Calculate the average value of a list of numbers"""

import csv
import os
import sys
from statistics import mean

from ExecutionTimer import ExecutionTimer
from rich import box
from rich.console import Console
from rich.table import Table

FILE = "/tmp/hwinfo.csv"


def main(csv_file):
    table = Table(
        title=os.path.split(csv_file)[-1],
        show_lines=True,
        box=box.HEAVY_EDGE,
        show_header=True,
        header_style="bold on gray27",
        style="cyan on gray30",
    )
    table.add_column("Sensor", justify="left", style="bold on grey27", no_wrap=True)
    table.add_column("Min", style="green on grey30", justify="right")
    table.add_column("Mean", style="yellow on grey30", justify="right")
    table.add_column("Max", style="red on grey30", justify="right")

    with open(csv_file) as f:
        reader = csv.reader(f)
        header = next(reader)

        if len(header) == 1:  # Single column file
            numbers = [float(row[0]) for row in reader]
            avg = round(mean(numbers), 3)
            print(avg)
            sys.exit(0)

        else:  # Multiple columns
            data = list(zip(*reader, strict=False))  # Transpose the data so we can access by column

    for i, col in enumerate(header):
        if i == 0:
            # Skip datetime col
            continue
        try:
            numbers = [float(x) for x in data[i] if "Network is unreachable" not in x]
            min_value = round(min(numbers), 2) if min(numbers) < 13 else int(min(numbers))
            max_value = round(max(numbers), 2) if max(numbers) < 13 else int(max(numbers))
            mean_value = round(mean(numbers), 2) if mean(numbers) < 13 else int(mean(numbers))
            table.add_row(
                col.strip().upper().replace("_", " "),
                str(min_value),
                str(mean_value),
                str(max_value),
            )
            # print(
            #     f"\x1b[1m{col.strip()}:\x1b[0m\n min: {min_value}\n max: {max_value}\n mean: {mean_value}",
            #     end="\n\n",
            # )
        except (IndexError, ValueError) as e:
            print("Error processing column", col, ": ", str(e), sep="")

        # TODO : Pretty print output
    console = Console()
    console.print(table)


if __name__ == "__main__":
    with ExecutionTimer():
        if len(sys.argv) > 1:
            FILE = sys.argv[1]  # Use the file given as argument, if any
        main(FILE)
