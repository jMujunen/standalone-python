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

def printhelp(fdesc):
    print("""
Usage:
    python hex2rgb.py <hex code>
    echo <hex code> | python hex2rgb.py # Reads from stdin
    python hex2rgb.py                   # Reads from clipboard
""", file=fdesc)

if __name__ == "__main__":
    match sys.argv[1:]:
        case ['-h' | '--help']:
            printhelp(sys.stdout)
            sys.exit(0)
        case [x]:
            rgb = hex_to_rgb(x)
        case [] | None:
            if sys.stdin.isatty():
                try:
                    arg = clipboard.paste()
                    rgb = hex_to_rgb(arg)
                except ValueError as e:
                    print(f'\033[31mError: \033[0m {arg} is not a valid hex code', file=sys.stderr)
                    printhelp(sys.stderr)
                    sys.exit(1)
            else:
                arg = sys.stdin.read().strip()
                rgb = hex_to_rgb(arg)
        case _:
            printhelp(sys.stderr)
            sys.exit(1)

    print(str(rgb))
    clipboard.copy(str(rgb))
    sys.exit(0)


