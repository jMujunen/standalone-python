#!/usr/bin/env python3

# sizeof.py - additianl functionality to `sizeof` bash alias

import os
import subprocess
import sys
import argparse

from human_bytes import convert_bytes

def parse_args():
    parser = argparse.ArgumentParser(
        description='Additianl functionality to `sizeof` bash alias',
        usage='sizeof.py OPTIONS ... PATH',
    )
    parser.add_argument('path', nargs='?', default='.', 
        help='Path to directory. Defaults to current directory.')
    args = parser.parse_args()
    return args

def sizeof(path):
    output = subprocess.run(
        f'du {path} | tail -1',
        shell=True,
        capture_output=True,
        text=True
    )

    stdout = output.stdout.strip()
    stderr = output.stderr.strip()
    if not 'denied' in stderr:
        print(stderr)
    size, directory = stdout.split('\t')
    print(convert_bytes(int(size)))
    return stdout, stderr if stderr else stdout


def all_direcorty_sizes(self, path):
    total = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total += os.path.getsize(fp)
    return total
def all_file_sizes(self, path):
    total = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total += os.path.getsize(fp)
    return total


# Example usage
if __name__ == '__main__':
    args = parse_args()
    sizeof(args.path)
