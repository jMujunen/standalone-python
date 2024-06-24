import os
import sys
import argparse
import re
import matplotlib.pyplot as plt

DIGITS_RE = re.compile(r'(\d+(\.\d+)?)')
ALL_COLUMNS_KEYWORDS = ["all", "-all", "--all", "-all", "-a", 
                         "all columns", "all_columns", "all columns", "all_columns"]
def parse_args():
    parser = argparse.ArgumentParser(description="Generate a graph from numbers in a file.", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("FILE", help="Enter the file name", type=str)
    parser.add_argument("-c", "--column", help='''If input is a csv file, choose which column to graph. Valid values are str(header) or int(header) Examples: - graph.py /tmp/cpu_data.csv -c 1 - graph.py /tmp/cpu_data.csv -c "average_clock"''', nargs="+")
    return parser.parse_args()

def main(args):
    try:
        with open(args.FILE) as file:
            header = next(file).strip().split(",")
            
            if args.column:
                for column in args.column:
                    try:
                        # Processes all columns if `all|-all|--all`  is passed
                        if column in ALL_COLUMNS_KEYWORDS:
                            numbers = [float(x) for x in DIGITS_RE.findall(''.join(file))]
                            plt.plot(numbers)
                            plt.show()
                            return
                        
                        # Processing specific column
                        column = int(column) if column.isdigit() else column
                        numbers = [float(x.split(',')[header.index(str(column))]) for x in file]
                        plt.plot(numbers)
                        plt.show()
                    except Exception as e:
                        print('Invalid column type')
                        sys.exit(1)
            else:
                numbers = [float(x) for line in file for x in DIGITS_RE.findall(line)]
                plt.plot(numbers)
                plt.show()
        sys.exit(0)
    except KeyboardInterrupt:
        sys.exit(1)
        
if __name__ == "__main__":
    args = parse_args()
    main(args)import os
import sys
import argparse
import re
import matplotlib.pyplot as plt

DIGITS_RE = re.compile(r'(\d+(\.\d+)?)')
ALL_COLUMNS_KEYWORDS = ["all", "-all", "--all", "-all", "-a", 
                         "all columns", "all_columns", "all columns", "all_columns"]
def parse_args():
    parser = argparse.ArgumentParser(description="Generate a graph from numbers in a file.", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("FILE", help="Enter the file name", type=str)
    parser.add_argument("-c", "--column", help='''If input is a csv file, choose which column to graph. Valid values are str(header) or int(header) Examples: - graph.py /tmp/cpu_data.csv -c 1 - graph.py /tmp/cpu_data.csv -c "average_clock"''', nargs="+")
    return parser.parse_args()

def main(args):
    try:
        with open(args.FILE) as file:
            header = next(file).strip().split(",")
            
            if args.column:
                for column in args.column:
                    try:
                        # Processes all columns if `all|-all|--all`  is passed
                        if column in ALL_COLUMNS_KEYWORDS:
                            numbers = [float(x) for x in DIGITS_RE.findall(''.join(file))]
                            plt.plot(numbers)
                            plt.show()
                            return
                        
                        # Processing specific column
                        column = int(column) if column.isdigit() else column
                        numbers = [float(x.split(',')[header.index(str(column))]) for x in file]
                        plt.plot(numbers)
                        plt.show()
                    except Exception as e:
                        print('Invalid column type')
                        sys.exit(1)
            else:
                numbers = [float(x) for line in file for x in DIGITS_RE.findall(line)]
                plt.plot(numbers)
                plt.show()
        sys.exit(0)
    except KeyboardInterrupt:
        sys.exit(1)
        
if __name__ == "__main__":
    args = parse_args()
    main(args)