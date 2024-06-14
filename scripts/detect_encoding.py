#!/usr/bin/env python3
"""Detects the encoding of the given text file."""

import argparse

import chardet


def parse_args():
    """
    Parse command line arguments.

    Returns:
    --------
         args: The parsed arguments.
    """
    parser = argparse.ArgumentParser(description='Detect the encoding of a text based file')
    parser.add_argument('file_path', type=str, help='The path to the text file')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose mode')
    return parser.parse_args()


def main(file):
    """
    Detects the encoding of the given text file.

    Args:
    -----
        file_path (str): The path to the text file.

    Returns:
    ---------
        str: The detected encoding.
    """
    with open(file, 'rb') as f:
        encoding = chardet.detect(f.read())['encoding']
    return encoding


if __name__ == "__main__":
    args = parse_args()
    result = main(args.file_path)
    # TODO M0R3 Verbose
    if args.verbose:
        print(f'Input file: {args.file_path}')
    print(result)
