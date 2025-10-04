#!/usr/bin/env python3
"""Convert hex or RGB color codes to ascii escape codes."""

import argparse
import random
import re
import sys
from collections.abc import Generator
from re import Pattern
from typing import Any

import clipboard


def rgb_to_ascii(r: int, g: int, b: int) -> str:
    r"""Convert RGB color values to an ascii escape code.

    >>> rgb_to_ascii(255, 0, 0)
    $ '\x1b[38;2;255;0;0m'"""
    return f"\033[38;2;{r};{g};{b}m"


def random_hex() -> str:
    """Generate a random hexadecimal color code."""
    return f"#{random.randint(0, 255):02x}{random.randint(0, 255):02x}{random.randint(0, 255):02x}"


def hex_to_rgb(hex_code: str) -> tuple[int, ...]:
    """Convert a hexadecimal color code to an RGB tuple.

    >>> hex_to_rgb("#FFFFFF")
    $ (255, 255, 255)
    """
    hex_code = hex_code.lstrip("#")
    return tuple(int(hex_code[i : i + 2], 16) for i in (0, 2, 4))


def hex_to_ascii(hex_code: str) -> str:
    r"""Convert a hexadecimal color code to its ascii equivalent.

    >>> hex_to_ascii("#FF0000")
    $ '\x1b[38;2;255;0;0m'"""
    rgb = hex_to_rgb(hex_code)
    return rgb_to_ascii(*rgb)


def rgb_to_hex(rgb: tuple[int | str, ...]) -> str:
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def generate_fade(
    hex_code: str, steps: int = 10, start: str = "FFFFFF", end: str = "000000"
) -> list[str]:
    """Generate a list of hexadecimal color codes that transition smoothly
    from white (#FFFFFF) to the given color (hex_code) and then back to black (#000000).

    Parameters
    -----------
        hex_code (str): The target hexadecimal color code.
        steps (int, optional): Number of steps in the fade. Default is 10.
        start_color (str, optional): The starting hexadecimal color code. Default is "FFFFFF".
        end_color (str, optional): The ending hexadecimal color code. Default is "000000".

    Returns
    -------
        list[str]: A list of hexadecimal color codes representing the fade.
    """

    def hex_to_rgb(hex_code: str) -> tuple[int, ...]:
        hex_code = hex_code.lstrip("#")
        return tuple(int(hex_code[i : i + 2], 16) for i in (0, 2, 4))

    start_color: tuple[int, ...] = hex_to_rgb(start)
    mid_color: tuple[int, ...] = hex_to_rgb(hex_code)
    end_color: tuple[int, ...] = hex_to_rgb(end)

    def formula_template(a: int, x: int, y: int) -> float:
        return a + (x - y) * i / steps

    fade_to_mid: list[str] = []
    fade_from_mid: list[str] = []

    # Generate fade from white to mid color
    for _ in range(steps + 1):
        # r,g,b
        r, g, b = (
            formula_template(start_color[0], mid_color[0], end_color[0]),
            formula_template(start_color[1], mid_color[1], end_color[1]),
            formula_template(start_color[2], mid_color[2], end_color[2]),
        )
        fade_to_mid.append(rgb_to_hex((r, g, b)))

    # Generate fade from mid color to black
    for i in range(steps + 1):
        r = int(mid_color[0] + (end_color[0] - mid_color[0]) * i / steps)
        g = int(mid_color[1] + (end_color[1] - mid_color[1]) * i / steps)
        b = int(mid_color[2] + (end_color[2] - mid_color[2]) * i / steps)
        fade_from_mid.append(rgb_to_hex((r, g, b)))

    # Combine the two fades, removing the duplicate mid color
    return fade_to_mid[:-1] + fade_from_mid


def main(input_string: str) -> Generator:
    """Parse the color input based on the format (RGB or Hex)."""
    rgb_regex: Pattern[str] = re.compile(r"\d{1,2},\s*\d{1,3},\s*\d{1,3}")
    hex_regex: Pattern[str] = re.compile(r"#?(?:[0-9a-fA-F]{3}){2}")

    rgb_matches: list[str] = rgb_regex.findall(input_string)
    hex_matches: list[str] = hex_regex.findall(input_string)

    for match in rgb_matches:
        rgb = map(int, re.findall(r"\d+", match))
        ascii_code = rgb_to_ascii(*rgb)
        stripped_ascii_code = ascii_code.replace("\033", "")
        print(f"{ascii_code}{match} - {stripped_ascii_code}\033[0m")
        yield stripped_ascii_code

    for match in hex_matches:
        ascii_code: str = hex_to_ascii(match)
        stripped_ascii_code = ascii_code.replace("\033", "")
        print(f"{ascii_code}{match} - {stripped_ascii_code}\033[0m")
        yield stripped_ascii_code


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Performs a non-greedy regex search on the given string and renders each hex or rbg color found",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "input",
        help="Input source (clipboard or file)",
        default="clipboard",
        nargs="+",
    )
    parser.add_argument(
        "--copy",
        action="store_true",
        help="Copy results to clipboard",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if args.input[0] == "clipboard":
        input_txt = clipboard.paste()
    elif args.input[0] == "file":
        if len(args.input) != 2:
            print("Error: Please provide a file path", file=sys.stderr)
            sys.exit(1)
        file_path = args.input[1]
        with open(file_path, encoding="utf-8") as file:
            input_txt = file.read()
    else:
        sys.exit(1)

    for result in main(input_txt):
        if args.copy:
            clipboard.copy(result)
    sys.exit(0)
