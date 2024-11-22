#!/usr/bin/env python3
import csv
import sys
from pathlib import Path
from statistics import mean

from ExecutionTimer import ExecutionTimer
from rich import box
from rich.console import Console
from rich.table import Table

FILE = "/tmp/hwinfo.csv"
INTERVAL = 60  # 60/second, 3600/hour


def main(csv_file: str | Path) -> None:
    file = Path(csv_file)
    table = Table(
        title=file.name,
        # show_lines=True,
        box=box.ROUNDED,
        show_header=True,
        header_style="bold",
        style="#343f44",
    )
    table.add_column("Sensor", justify="left", style="bold", no_wrap=True)
    table.add_column("Min", style="green", justify="right")
    table.add_column("Mean", style="yellow", justify="right")
    table.add_column("Max", style="red", justify="right")

    with file.open() as f:
        reader = csv.reader(f)
        header = next(reader)

        if len(header) == 1:  # Single column file
            numbers = [float(row[0]) for row in reader]
            avg = round(mean(numbers), 3)
            print(avg)
            return
        reader = list(reader)
        num_rows = len(reader)
        data = list(zip(*reader, strict=False))  # Transpose the data so we can access by column

    parsed_data = {}
    for i, col in enumerate(header):
        if i == 0:
            # Skip datetime col
            continue
        try:
            numbers = [float(x) for x in data[i] if "Network is unreachable" not in x and x]
            min_value = round(min(numbers), 2) if min(numbers) < 13 else int(min(numbers))
            mean_value = round(mean(numbers), 2) if mean(numbers) < 13 else int(mean(numbers))
            max_value = round(max(numbers), 2) if max(numbers) < 13 else int(max(numbers))

            parsed_data[col] = (min_value, mean_value, max_value)
        except (IndexError, ValueError) as e:
            print("Error processing column", col, ": ", str(e), sep="")
    for column, values in sorted(parsed_data.items()):
        min_v, mean_v, max_v = values
        table.add_row(
            column.strip().upper().replace("_", " "),
            str(min_v),
            str(mean_v),
            str(max_v),
        )

    hours, minutes = divmod(num_rows, INTERVAL * 60)
    minutes, _ = divmod(minutes, INTERVAL)
    table.add_section()
    table.add_row(
        "TOTAL",
        f"{hours}h",
        f"{minutes}m",
        str(num_rows),
        style="bold #d3c7ac",
    )
    console = Console()
    console.print(table)


if __name__ == "__main__":
    with ExecutionTimer():
        if len(sys.argv) > 1:
            FILE = sys.argv[1]  # Use the file given as argument, if any
        main(FILE)
    sys.exit()
