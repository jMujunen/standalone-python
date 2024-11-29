#!/usr/bin/env python3


import argparse
import re
from pathlib import Path

import clipboard
from fsutils.dir import Dir
from fsutils.utils import FILE_TYPES

mime = FILE_TYPES

hex_regex = re.compile(r"#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})")


def get_escape_sequence(hex: str) -> str:
    r"""Convert a hexadecimal color code to its ANSI equivalent.

    >>> get_escape_sequence("#FF0000")
    $ '\x1b[38;2;255;0;0m'"""
    hex_code = hex.lstrip("#")
    rgb = tuple(int(hex_code[i : i + 2], 16) for i in (0, 2, 4))
    return "\033[38;2;{};{};{}m".format(*rgb)


def main() -> None:
    path = Dir("~/.themes")

    txtfiles = list(
        filter(
            lambda x: all(
                (
                    x.suffix not in mime["video"],
                    x.suffix not in mime["img"],
                    x.suffix not in {".svg", ".rc", ""},
                ),
            ),
            path.file_objects,
        )
    )
    text = ""
    for file in txtfiles:
        try:
            text += file.read_text()
        except Exception as e:
            print("\x1b[31m", str(e), "\x1b[0m")
    lines = text.splitlines()

    # Parse each line to see if it's a color code
    colors = [i[0] for i in [hex_regex.findall(line) for line in lines] if i]

    for color in colors:
        try:
            print(f"{get_escape_sequence(color)}{color}", end="\x1b[0m\t")
        except Exception as e:
            print("\x1b[31m", str(e), "\x1b[0m")


if __name__ == "__main__":
    main()
