#!/usr/bin/env python3

# find_duplicate_files.py - Find duplicate files in two directories

import os
import argparse
import glob
import sys

from pb import ProgressBar
from ExecutionTimer import ExecutionTimer

def parse_arguments():
    parser = argparse.ArgumentParser(description="Find and remove duplicate files from two directories")
    parser.add_argument("dir_remove", help="Path to the first directory where the duplicate files will be removed")
    parser.add_argument("dir_keep", help="Path to the second directory where the duplicate files will be kept")
    # Add option for recursive mode
    parser.add_argument("-r", "--recursive", action="store_true", help="Enable recursive mode")
    return parser.parse_args()


# Function to iterate files in a directory and return a list of file names
def get_files_in_directory(directory, recursive):
    file_count = 0
    try:
        if recursive:
            files = []
            for root, _, filenames in os.walk(directory):
                for filename in filenames:
                    if os.path.isfile(os.path.join(root, filename)):
                        file_count +=1
                        files.append(str(filename).replace('_output', ''))
                        print(f'Files found in {directory}: {file_count}', end="\r")
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
def find_common_files(directory_remove, directory_keep, recursive):
    print("Finding common files...", end="\n")
    try:
        if recursive:
            common_files = []
            files1 = get_files_in_directory(directory_remove, recursive)
            print('\n----------------------------------------')
            files2 = get_files_in_directory(directory_keep, recursive)
            print('\n----------------------------------------')
            print('Comparing files...')
            with ExecutionTimer():
                for file1 in files1:
                    if file1 in files2:
                        common_files.append(os.path.basename(file1))
            return common_files

        else:
            with ExecutionTimer():
                common_files = []
                files1 = get_files_in_directory(directory_remove, recursive)
                files2 = get_files_in_directory(directory_keep, recursive)
                for file1 in files1:
                    if file1 in files2:   
                        common_files.append(os.path.basename(file1))       
            return common_files

    except:
        print("Error: Problem finding common files")
        #sys.exit(1)


def remove_files_recusivly(directory, duplicate_files_list):
    try:
        tasks = len(duplicate_files_list)
        print(f"Removing {tasks} common files...")
        progress = ProgressBar(tasks)
    except:
        print('Error initializing progress bar')
    try:
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file in duplicate_files_list:
                    progress.increment()
                    os.remove(os.path.join(root, file))
        return 0
    except:
        print('Error removing files')
        return 1

# Example usage
if __name__ == "__main__":
    # Parse command line arguments
    args = parse_arguments()
    directory_remove = args.dir_remove
    directory_keep = args.dir_keep
    recursive = args.recursive

    # Find common files
    common_files_list = find_common_files(directory_remove, directory_keep, recursive)
    # Remove common files
    runtime_code = remove_files_recusivly(directory_remove, common_files_list)

    # Check the return code and print a helpful message
    if runtime_code == 0:
        print("\nDone!")
    else:
        print(f'Error {runtime_code} : Something went wrong')
    