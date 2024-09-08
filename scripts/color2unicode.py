#!/usr/bin/env python3
"""Convert hex or RGB color codes to ANSI escape codes."""

import argparse
import random
import re

import clipboard


def rgb_to_ansi(r: int, g: int, b: int) -> str:
    r"""Convert RGB color values to an ANSI escape code.

    >>> rgb_to_ansi(255, 0, 0)
    $ '\x1b[38;2;255;0;0m'"""
    return f"\033[38;2;{r};{g};{b}m"


def random_hex() -> str:
    """Generate a random hexadecimal color code."""
    return f"#{random.randint(0, 255):02x}{random.randint(0, 255):02x}{random.randint(0, 255):02x}"


def hex_to_rgb(hex_code: str) -> tuple[int, ...]:
    """Convert a hex color code to a tuple of RGB color values.

    >>> hex_to_rgb("#FFFFFF")
    $ (255, 255, 255)"""
    hex_code = hex_code.lstrip("#")
    return tuple(int(hex_code[i : i + 2], 16) for i in (0, 2, 4))


def hex_to_ansi(hex_code: str) -> str:
    r"""Convert a hexadecimal color code to its ANSI equivalent.

    >>> hex_to_ansi("#FF0000")
    $ '\x1b[38;2;255;0;0m'"""
    rgb = hex_to_rgb(hex_code)
    return rgb_to_ansi(*rgb)


def main(color: str) -> None:
    """Parse the color input based on the format (RGB or Hex)."""
    color_input = color

    if re.match(r"^\d{1,3},\s*\d{1,3},\s*\d{1,3}$", color_input):
        # RGB format
        rgb_values = map(int, color_input.split(","))
        ansi_code = rgb_to_ansi(*rgb_values)
    elif re.match(r"\(\d{1,3},\s*\d{1,3},\s*\d{1,3}\)", color_input) or re.match(
        r"\('\d{1,3},\s*\d{1,3},\s*\d{1,3}'\)", color_input
    ):
        # RGB format
        rgb_values = re.findall(r"\d+", color_input)
        ansi_code = rgb_to_ansi(*rgb_values)
    elif re.match(r"^#(?:[0-9a-fA-F]{3}){1,2}$", color_input):
        # Hex format
        ansi_code = hex_to_ansi(color_input)
    else:
        print("Invalid input format. Please enter a valid RGB or hex color code.")
        return
    stripped_ansi_code = ansi_code.replace("\033", "")
    print(f"{ansi_code}{stripped_ansi_code}\033[0m")
    clipboard.copy(stripped_ansi_code)


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Convert hex or RGB color codes to ANSI escape codes."
    )
    parser.add_argument(
        "color",
        help='Enter RGB color code as "R,G,B" or hex color code as "#RRGGBB" or "#RGB"',
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    main(args.color)
