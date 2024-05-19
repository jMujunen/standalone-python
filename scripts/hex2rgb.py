#!/usr/bin/env python3

import sys

def hex_to_rgb(hex_code):
    """
    Convert a hex color code to a tuple of RGB color values.

    Parameters:
        hex_code (str): Hex color code string starting with '#'.

    Returns:
        tuple: Tuple of integers representing the RGB components of the color.

    Example:
        >>> hex_to_rgb("#FFFFFF")
        Reurns:  (255, 255, 255)

    """
    hex_code = hex_code.lstrip("#")
    return tuple(int(hex_code[i : i + 2], 16) for i in (0, 2, 4))

# Example
if __name__ == "__main__":
    if len(sys.argv) == 2:
        print(hex_to_rgb(sys.argv[1]))
        sys.exit(0)
    else:
        print("Usage: python hex2rgb.py <hex code>")
        sys.exit(1)
