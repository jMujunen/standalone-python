#!/usr/bin/env python3
"""Convert a hex color code to a tuple of RGB color values."""

import sys
import pyperclip


def hex_to_rgb(hex_code):
    """
    Example:
    --------
        >>> hex_to_rgb("#FFFFFF")
        Reurns:  (255, 255, 255)

    """
    hex_code = hex_code.lstrip("#")
    return tuple(int(hex_code[i : i + 2], 16) for i in (0, 2, 4))


if __name__ == "__main__":
    if len(sys.argv) == 2:
        rgb = hex_to_rgb(sys.argv[1])
        print(rgb)
        pyperclip.copy(str(hex))
        sys.exit(0)
    print("Usage: python hex2rgb.py <hex code>")
    sys.exit(1)
