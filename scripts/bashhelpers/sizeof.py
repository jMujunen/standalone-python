#!/usr/bin/env python3

# sizeof.py - additianl functionality to `sizeof` bash alias

import os
import subprocess
import sys
import argparse

from ByteConverter import ByteConverter

def parse_args():
    parser = argparse.ArgumentParser(
        description='Additianl functionality to `sizeof` bash alias',
        usage='sizeof.py [-l LINES] ... PATH',
    )
    parser.add_argument('path', nargs='?', default='.', 
        help='Path to directory. Defaults to current directory.')
    parser.add_argument('-l', '--lines', type=int, default=1)
    args = parser.parse_args()
    return args


def sizeof(path):
    output = subprocess.run(
        f'du -b {path} | sort -h | tail -{int(args.lines)}',
        shell=True,
        capture_output=True,
        text=True
    )

    stdout = output.stdout.strip()
    stderr = output.stderr.strip()
    if not 'denied' in stderr:
        print(stderr)
    output = stdout.split('\n')
    for item in output:
        size, directory = item.split('\t')
        print(f'{ByteConverter.convert_bytes(int(size)).ljust(12)}{directory}')
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
