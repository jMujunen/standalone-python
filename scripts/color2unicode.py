#!/usr/bin/env python3

# ascii_color.py - Convert hex or RGB color codes to ANSI escape codes

import argparse
import re
import pyperclip
import random

def rgb_to_ansi(r, g, b):
    """
    Convert RGB color values to an ANSI escape code.

    Parameters:
        r (int): Red component of the color, in range 0-255.
        g (int): Green component of the color, in range 0-255.
        b (int): Blue component of the color, in range 0-255.


    Returns:
        str: ANSI escape code string for the given RGB color.

    Example:
        >>> rgb_to_ansi(255, 0, 0)
        Returns: '\x1b[38;2;255;0;0m'
    """
    # if isinstance(args[0], str) and len(args[0]) > 5:
    #     r, g, b = args[0].split(',')
    # r, g, b = args
    return f"\033[38;2;{r};{g};{b}m"


def random_hex():
    """
    Generate a random hexadecimal color code.

    Returns:
        str: A randomly generated hexadecimal color code in the format "#RRGGBB", where RR, GG, and BB represent random integers between 0 and 255.

    Example:
        >>> random_hex()
        '#e0c1f8'
    """
    return "#%02x%02x%02x" % (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

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

def hex_to_ansi(hex_code):
    """
    Convert a hexadecimal color code to its ANSI equivalent.

    Parameters:
        hex_code (str): The hexadecimal color code to convert.

    Returns:
        str: The ANSI color code equivalent.

    Example:
        >>> hex_to_ansi("#FF0000")
        Returns: '\x1b[38;2;255;0;0m'

        '\x1b[38;2;255;0;0m'
    """
    rgb = hex_to_rgb(hex_code)
    return rgb_to_ansi(*rgb)


def main(color):
    # Parse the color input based on the format (RGB or Hex)
    color_input = color

    if re.match(r"^\d{1,3},\s*\d{1,3},\s*\d{1,3}$", color_input):
        # RGB format
        rgb_values = map(int, color_input.split(","))
        ansi_code = rgb_to_ansi(*rgb_values)
    elif re.match(r"\(\d{1,3},\s*\d{1,3},\s*\d{1,3}\)", color_input) or \
        re.match(r"\('\d{1,3},\s*\d{1,3},\s*\d{1,3}'\)", color_input):
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
    pyperclip.copy(stripped_ansi_code)



def parse_arguments():
    """
    Parse command line arguments.

    Returns:
        Parsed arguments.
    """
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
