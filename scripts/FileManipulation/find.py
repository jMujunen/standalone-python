#!/usr/bin/env python

# find.py - Find a file in a directory

import os
import os.path
import argparse

def find_file(name, path, case_sensitive, file_type):
    if file_type == 'd':
        files = (f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f)))
    elif file_type == 'f':
        files = (f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)))
    else:
        files = os.listdir(path)

    if case_sensitive:
        files = (f for f in files if f == name)
    else:
        files = (f for f in files if f.lower() == name.lower())

    for file in files:
        file_path = os.path.join(path, file)
        if os.path.islink(file_path):
            continue
        elif os.path.isfile(file_path) or os.path.isdir(file_path):
            return file_path

    return None

parser = argparse.ArgumentParser(description='Find a file in a directory.')
parser.add_argument('name', help='The name of the file to search for.')
parser.add_argument('path', help='The path to the directory to search in.')
parser.add_argument('-type', choices=['d', 'f'], help='The type of file to search for (d for directory, f for file).')
parser.add_argument('-iname', action='store_true', help='Perform a case-insensitive search.')
args = parser.parse_args()

print(find_file(args.name, args.path, not args.iname, args.type))
