#!/usr/bin/env python3
"""Convert hex or RGB color codes to ascii escape codes."""

import argparse
import random
import re

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


def generate_fade(hex_code: str, steps=10, start_color="FFFFFF", end_color="000000") -> list[str]:
    """Generate a list of hexadecimal color codes that trasciition smoothly
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

    def hex_to_rgb(hex_code: str) -> tuple:
        hex_code = hex_code.lstrip("#")
        return tuple(int(hex_code[i : i + 2], 16) for i in (0, 2, 4))

    start_color = hex_to_rgb(start_color)
    mid_color = hex_to_rgb(hex_code)
    end_color = hex_to_rgb(end_color)

    def formula_template(a, x, y):
        return a + (x - y) * i / steps

    fade_to_mid = []
    fade_from_mid = []

    # Generate fade from white to mid color
    for i in range(steps + 1):
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


def main(color: str) -> None:
    """Parse the color input based on the format (RGB or Hex)."""
    color_input = color
    rbg_regex = re.compile(r"[1-2]\d{2}|\d{1,2},\s*\d{1,3},\s*\d{1,3}")
    if rbg_regex.match(color_input):
        # RGB format
        rgb_values = map(int, color_input.split(","))
        ascii_code = rgb_to_ascii(*rgb_values)
        # RGB format
        rgb_values = re.findall(r"\d+", color_input)
        ascii_code = rgb_to_ascii(*rgb_values)
    elif re.match(r"^#(?:[0-9a-fA-F]{3}){1,2}$", color_input):
        # Hex format
        ascii_code = hex_to_ascii(color_input)
    else:
        print("Invalid input format. Please enter a valid RGB or hex color code.")
        return
    stripped_ascii_code = ascii_code.replace("\033", "")
    print(f"{ascii_code}{stripped_ascii_code}\033[0m")
    clipboard.copy(stripped_ascii_code)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Manipulate and modify colors.")
    parser.add_argument(
        "color",
        help='Enter RGB color code as "R,G,B | R G B" or hex color code as "#RRGGBB"',
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    main(args.color)
