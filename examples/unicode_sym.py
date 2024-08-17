#!/usr/bin/env python3
"""unicode_sym.py - Return unicode symbols from a number."""

import sys


def main(num):
    return f"\\U{num:04X}"


if __name__ == "__main__":
    num = int(sys.argv[1])
    print(main(num))
