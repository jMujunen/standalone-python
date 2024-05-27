#!/usr/bin/env python3

import argparse
import chardet

def parse_args():
    """
    Parse command line arguments.

    Returns:
    - args (argparse.Namespace): The parsed arguments.
    """
    parser = argparse.ArgumentParser(description='Detect the encoding of a text based file')
    parser.add_argument('file_path', type=str, help='The path to the text file')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose mode')
    args = parser.parse_args()
    return args

def detect_encoding(file_path):
    """
    Detects the encoding of the given text file.

    Args:
    -----
        file_path (str): The path to the text file.

    Returns:
    ---------
        str: The detected encoding.
    """
def detect_encoding(file):
    with open(file, 'rb') as f:
        encoding = chardet.detect(f.read())['encoding']
    return encoding


def __main__():
    args = parse_args()
    encoding = detect_encoding(args.file_path)
    if args.verbose:
        print(f'Input file: {args.file_path}')
    print(encoding)

