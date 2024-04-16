#!/usr/bin/env python3

# remove_files_in_list.py - Remove files in a list from a directory

import os
import argparse

def parse_arguments():
    parser = argparse.ArgumentParser(description="Remove files from a provided list from a provided directory")
    parser.add_argument("data", help="Data [LIST] to be removed from a directory")
    parser.add_argument("dir", help="Path to the directory where files will be removed")
    parser.add_argument("-r", "--recursive", action="store_true", help="Enable recursive mode")
    return parser.parse_args()

def remove_files_in_list(directory, data):
    if os.path.isfile(data):
        with open (data, 'r') as f:
            for line in f:
                print(f'Removing {line}')
                try:
                    os.remove(os.path.join(directory, line.strip()))
                except FileNotFoundError as e:
                    print(e)
                    continue
    elif type(data) == list:
        for line in data:
            print(f'Removing {line}')
            os.remove(os.path.join(directory, line.strip()))
    else:
        print(f'Error. Is {data} a file or a list?')
def remove_files_in_list_recusivly(directory, data):
    list_of_files_to_remove = []

    if os.path.isfile(data):
        with open (data, 'r') as f:
            for line in f:
                list_of_files_to_remove.append(line.strip())
    '''
    elif type(data) == list:
        for line in data:
            list_of_files_to_remove.append(line)
    '''   
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file in list_of_files_to_remove:
                print(f'Removing {file}')
                os.remove(os.path.join(root, file))

# Example useage
if __name__ == "__main__":
    args = parse_arguments()
    directory = args.dir
    data = args.data

    if args.recursive:
        remove_files_in_list_recusivly(directory, data)
    else:
        remove_files_in_list(directory, data)