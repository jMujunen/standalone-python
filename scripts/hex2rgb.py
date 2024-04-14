#!/usr/bin/env python3

import argparse
def hex_to_rgb(hex):
  return tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))

def parse_arguments():
    """
    Parse command line arguments.

    Returns:
        Parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="Convert HEX to RGB"
    )
    parser.add_argument(
        "color",
        help='Enter HEX color code as "#RRGGBB"',
    )

    return parser.parse_args()

# Example
if __name__ == "__main__":
    args = parse_arguments()
    print(hex_to_rgb(args))


