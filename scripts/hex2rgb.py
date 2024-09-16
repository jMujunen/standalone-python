#!/usr/bin/env python3
"""Convert a hex color code to a tuple of RGB color values."""

import sys

import clipboard


def hex_to_rgb(hex_code) -> tuple[int, ...]:
    """Convert a hex color code to an RGB tuple.

    Example:
    --------
        >>> hex_to_rgb("#FFFFFF")
        Reurns:  (255, 255, 255)

    """
    hex_code = hex_code.lstrip("#")
    return tuple(int(hex_code[i : i + 2], 16) for i in (0, 2, 4))


if __name__ == "__main__":
    match len(sys.argv[1:]):
        case 1:
            rgb = hex_to_rgb(sys.argv[1])
        case 0:
            if sys.stdin.isatty():
                rgb = hex_to_rgb(clipboard.paste())
            else:
                rgb = hex_to_rgb(sys.stdin.read().strip())
        case _:
            print("Usage: python hex2rgb.py <hex code>", file=sys.stderr)
            sys.exit(1)

    print(f"{rgb}")
    clipboard.copy(str(rgb))
    sys.exit(0)
