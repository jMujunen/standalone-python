#!/usr/bin/env python3

# cpu_clocks.py - Measure CPU clocks

from time import sleep

import sys
import subprocess
import argparse
import os
import re
from datetime import datetime

def parse_args():
    parser = argparse.ArgumentParser(description='Measure CPU clocks')
    parser.add_argument('-d', '--duration', type=int, default=80, help='Measurement duration in seconds')
    parser.add_argument('-i', '--interval', type=float, default=0.2, help='Measurement interval in seconds')
    parser.add_argument('-o', '--output', type=str, default='/home/joona/Logs/cpu_clocks.csv', help='File output path')
    return parser.parse_args()


def write_data_to_file(csv_data, output_file):
    while True:
        try:
            with open (output_file, 'a') as f:
                f.writelines(csv_data)
                f.close()
        except KeyboardInterrupt:
            break

def query_cpu_clocks():
    processors = []
    clocks = []
    line = []
    # Read the contents of /proc/cpuinfo
    with open ('/proc/cpuinfo', 'r') as f:
        raw_output = f.read()
        f.close()

    # Define regex pattern
    regex_pattern = re.compile(r'(cpu MHz)\s+:\s+([\d.]+)')
    # Find all matches in the text
    matches = re.findall(regex_pattern, raw_output)

    dt = str(datetime.now())[:-7]  

    # Process the matches
    for match in matches:
        processors.append(match[0])      # Processor number
        clocks.append(match[1])          # CPU MHz
        
    # query = zip(processors, clocks)
    # data = list(query)

    line.append(dt)

    for clock in clocks:
        line.append(str(round(float(clock))))
    return line

def main():
    # Define headers
    header = [
        'datetime', 'cpu1', 'cpu2', 'cpu3', 'cpu4', 'cpu5', 'cpu6', 
        'cpu7', 'cpu8', 'cpu9', 'cpu10', 'cpu11', 'cpu12', 'cpu13', 
        'cpu14', 'cpu15', 'cpu16', 'cpu17', 'cpu18', 'cpu19', 'cpu20'
        ]

    data = []
    data.append(','.join(header))

    # Parse arguments
    args = parse_args()

    # Ensure filename includes .csv extension
    if "csv" not in args.output:
        args.output = f"{args.output}.csv"

    # Check if the output file already exists
    if os.path.exists(args.output):
        print(f'File {args.output} already exists')
        overwrite_answer = input('Do you want to overwrite it? ([Y]/n): ')
        if overwrite_answer.lower() == 'n':
            print('Exiting...')
            sys.exit(1)
    
    with open(args.output, 'w') as f:
        f.write(f"{','.join(header)}\n")
        f.close()
    # Get data and append to `data` in csv format
    # TODO - Print difrerent color for header
    for i in range(args.duration):
        print(f'[\033[38;2;57;206;196m {i + 1}/{args.duration} \033[0m] \033[1;32m {data[i]} \033[0m')
        with open(args.output, 'a') as f:
            f.write(f"{','.join(query_cpu_clocks())}\n")
        data.append(','.join(query_cpu_clocks()))
        sleep(args.interval)

    #write_data_to_file(data, args.output)

if __name__ == '__main__':
    main() 
    ''' 
    Defaults:
        python3 cpu_clocks.py
            --duration=80 
            --interval=0.2 
            --output=/home/joona/Logs/cpu_clocks.csv
    '''

