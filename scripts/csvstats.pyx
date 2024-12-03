#!/usr/bin/env python3
import csv
import sys
from pathlib import Path
from statistics import mean

from ExecutionTimer import ExecutionTimer
from rich import box
from rich.console import Console
from rich.table import Table
import io
from concurrent.futures import ThreadPoolExecutor

cdef public str args
cdef public unicode file = u"/tmp/hwinfo.csv"
# cdef public char* FILE = "/tmp/hwinfo.csv".encode('utf-8')
cdef public unsigned short int INTERVAL = 60  # 60/second, 3600/hour

cdef tuple[list[bytes], bytes] read_file(unicode file_path, unsigned int chunk_size=131072):
    cdef bytes partial_line, line, header
    cdef unsigned short int aggregate_size = 2048
    cdef list aggregated_lines = []
    partial_line = b''

    with open(file_path, 'rb') as f:
        # header = next(csv.reader(f))
        bufferedReader = io.BufferedReader(f) # type: ignore
        header = next(f)
        while True:
            chunk = bufferedReader.read(chunk_size)
            if not chunk:
                break
            # Combine the partial line from the previous chunk with the current chunk
            combined_chunk = partial_line + chunk
            # Split the combined chunk into lines
            lines = combined_chunk.split(b'\n')
            # The last line might be a partial line, so keep it for the next iteration
            partial_line = lines[-1]
            # Process all complete lines except the last one (which might be partial)
            for line in lines[:-1]:
                aggregated_lines.append(line)
        # Process any remaining partial line after the loop
        if partial_line:
            aggregated_lines.append(partial_line)
    return aggregated_lines, header


cdef tuple[dict[str, (float, float, float)], unsigned int] calculate_stats(list[bytes] content, bytes header):
    cdef dict parsed_data = {}
    cdef unsigned short int i
    cdef str col
    cdef list[float] numbers
    cdef unsigned int num_rows = len(content)
    cdef float min_value, mean_value, max_value

    cdef list[tuple[str]] data = list(zip(*(line.decode().split(', ') for line in content), strict=False))
    cdef list[str] decoded_header = header.decode().split(', ')
    for i, col in enumerate(decoded_header):
        if i == 0:
            continue
        try:
            numbers = [float(x) for x in data[i] if "Network is unreachable" not in x and x]
            min_value = min(numbers)
            mean_value = mean(numbers)
            max_value = max(numbers)
            # parsed_data[col] = numbers
            parsed_data[col] = (min_value, mean_value, max_value)
        except (IndexError, ValueError) as e:
            print("Error processing column ", col.strip(), ": ", str(e), sep="")
    return parsed_data, num_rows

cpdef void main(unicode csv_file):
    cdef list[bytes] content
    cdef bytes header

    cdef unsigned short int decimals = 1

    cdef str column
    cdef (float, float, float) values
    cdef float min_v, mean_v, max_v

    content, header = read_file(csv_file)
    cdef dict[str, (float, float, float)] result
    cdef unsigned int num_rows

    result, num_rows = calculate_stats(content, header)

    table = Table(
        title=csv_file,
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

    for column, values in sorted(result.items()):
        min_v, mean_v, max_v = values
        if 'voltage' in column:
            decimals = 2
        else:
            decimals = 0
        table.add_row(
            column.strip().upper().replace("_", " "),
            f'{min_v:.{decimals}f}',
            f'{mean_v:.{decimals}f}',
            f'{max_v:.{decimals}f}',
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

if __name__ == '__main__':
    args = ' '.join(sys.argv[1:])
    if len(args) > 0:
        file = args
    main(file)
