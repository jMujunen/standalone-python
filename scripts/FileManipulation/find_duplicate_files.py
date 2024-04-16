#!/usr/bin/env python3

# find_duplicate_files.py - Find duplicate files in two directories

import os
import argparse
import glob
import sys


def parse_arguments():
    parser = argparse.ArgumentParser(description="Find duplicate files in two directories")
    parser.add_argument("dir1", help="Path to the first directory")
    parser.add_argument("dir2", help="Path to the second directory")
    parser.add_argument("output", help="Path to the output file")
    # Add option for recursive mode
    parser.add_argument("-r", "--recursive", action="store_true", help="Enable recursive mode")
    return parser.parse_args()


# Function to iterate files in a directory and return a list of file names
def get_files_in_directory(directory, recursive):
    try:
        if recursive:
            files = []
            for root, _, filenames in os.walk(directory):
                for filename in filenames:
                    if os.path.isfile(os.path.join(root, filename)):
                        files.append(str(filename).replace('_output', ''))
            return files

        else:
            files = []
            files_in_directory = glob.glob(os.path.join(directory, '*'))
            for file in files_in_directory:
                if os.path.isfile(file):
                    files.append(str(os.path.basename(file)).replace('_output', ''))
            return files
    except:
        print("Error: Could not find the directory")
        sys.exit(1)
    '''
    for root, _, filenames in os.walk(directory):
        for filename in filenames:
            print(filename)
            files.append(os.path.join(root, filename))
    '''

# Function to compare two directories and return a list of common files
def find_common_files(directory1, directory2, recursive):
    try:
        if recursive:
            common_files = []
            files1 = get_files_in_directory(directory1, recursive)
            files2 = get_files_in_directory(directory2, recursive)
            for file1 in files1:
                if file1 in files2:   
                    common_files.append(os.path.basename(file1))
            return common_files

        else:
            common_files = []
            files1 = get_files_in_directory(directory1, recursive)
            files2 = get_files_in_directory(directory2, recursive)
            for file1 in files1:
                if file1 in files2:   
                    common_files.append(os.path.basename(file1))       
            return common_files

    except:
        print("Error: Problem finding common files")
        #sys.exit(1)

# Function to print a list to a file
def write_data_to_file(data, filepath):
    try:
        with open(filepath, 'w') as f:
            for item in data:
                f.write(f"{item}\n")
        return 0
    except:
        return 1

# Example usage
if __name__ == "__main__":
    # Parse command line arguments
    args = parse_arguments()
    directory1 = args.dir1
    directory2 = args.dir2
    output = args.output
    recursive = args.recursive
    # Find common files
    common_files_list = find_common_files(directory1, directory2, recursive)
    # Write data to file
    runtime_code = write_data_to_file(common_files_list, output)
    # Check the return code and print a helpful message
    try:
        os.system('clear')
    except:
        os.system('cls')

    if runtime_code == 0:
        print("Data written to file successfully")
    else:
        print(f'Error {runtime_code} : Could not write data to file')