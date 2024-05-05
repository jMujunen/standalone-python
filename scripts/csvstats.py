#!/usr/bin/env python3

# avgvalue.py - Calculate the average value of a list of numbers

import argparse
import sys
import os
import re

DIGIT_REGEX = re.compile(r'(\d+(\.\d+)?)')
FILE = "/tmp/hwinfo.csv"

def parse_args():
    parser = argparse.ArgumentParser(
        description="Calculates the min, max, and mean for each column in a csv file.\n\
            Also works on single column files.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "FILE", 
        help="Enter the file name",
        type=str
        )
    print('test')
    return parser.parse_args()

def main(csv_file):
    try:
        with open(csv_file) as file:
            header = next(file)
            content = file.readlines()
        
        
        if ',' in str(header):
            header = header.split(',')
        columns = [str(item) for item in header]

        # Single column file
        if len(columns) == 1:
            numbers = content
            numbers = [float(x) for x in numbers]
            avg = round(sum(numbers) / len(numbers), 3)
            print(avg)
            sys.exit(0)
            
        # Multiple column file (csv)
        c = []
        
        for column in columns:
            numbers = []
            for line in content:
                value = DIGIT_REGEX.findall(line.split(',')[header.index(column)])
                numbers.append(float(value[0][0]))

        
            min_value = round(min(numbers), 3)
            max_value = round(max(numbers), 3)
            mean_value = round(sum(numbers) / len(numbers), 3)

            print(f'''{column.strip()}: 
                min: {min_value}
                max: {max_value}
                mean: {mean_value}''')

        '''
            min_value = round(min(numbers), 3)
            max_value = round(max(numbers), 3)
            mean_value = round(sum(numbers) / len(numbers), 3)

            c.append([min_value, max_value, mean_value])
        
        print(' '.join(header).strip())
        print(print(' '.join([str(x) for x in c]).strip()))
        '''


        sys.exit(0)
    except Exception as e:
        print(e)
        pass

if __name__ == "__main__":
    if len(sys.argv) == 1:
        main(FILE)
    args = parse_args()
    main(args.FILE)