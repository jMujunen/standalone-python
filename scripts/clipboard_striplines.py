#!/usr/bin/env python3
"""Manipulate clipboard content."""

import argparse
import re
import sys
import clipboard

# TODO - add more presets for common patterns
PRESETS = {
    # Concatenate a multiline string into a single line separated a space
    "whitespace": lambda x: re.sub(r"(\n|\t|\s+)", " ", x, flags=re.MULTILINE).strip(),
    # Remove REPL prompt chars "...:"
    "ipy": lambda x: re.sub(r"(\.{3}:\s?|(In |Out)\[\d+\]:\s)", "", x, flags=re.MULTILINE),
    None: lambda x: x,
}


def main(pattern: str, replacement: str = "", preset: str | None = None) -> str:
    """Strip <pattern> from each line in the clipboard content.

    Paramters:
    ---------
        - `pattern(str)`: Character or pattern to strip. Can be any valid PCRE.
        - `replacement(str)`: Optional replacement string.
    """
    regex = re.compile(pattern)

    text = clipboard.paste()
    lines = text.splitlines()

    # Initialize an empty list to hold the processed lines
    output = []
    if preset is not None and preset in PRESETS:
        return PRESETS[args.preset](text)
    output = [re.sub(regex, replacement, line) for line in lines]
    # Join the output list back into a single text string
    return "\n".join(output)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Strips a character or string from each line, using the clipboard as I/O",
        usage="clip [OPTIONS] PATTERN",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""

        Example:
        -----------

        python3 clipboard_striplines.py wlan0 --replace=wlan1

        wlan0: authenticate        ->  wlan1: authenticate
        wlan0: send auth to        ->  wlan1: send auth to
        wlan0: authenticated       ->  wlan1: authenticated
        wlan0: associate with      ->  wlan1: associate with
        wlan0: RX AssocResp from   ->  wlan1: RX AssocResp from
        wlan0: associated          ->  wlan1: associated
        """,
    )
    parser.add_argument(
        "PATTERN",
        nargs="?",
        metavar="PATTERN",
        help="Pattern to search for and remove from each line",
        default=r"(^\s+|\s+$)",
    )
    parser.add_argument(
        "-r",
        "--replace",
        help="Replace character with this instead of stripping.",
        default="",
        type=str,
    )

    parser.add_argument(
        "--lstrip", help="Only strip from the left", action="store_true", default=False
    )

    parser.add_argument(
        "--rstrip", help="Only strip from the right", action="store_true", default=False
    )
    parser.add_argument("-l", "--list", help="List presets", action="store_true", default=False)
    parser.add_argument(
        "--preset",
        choices=PRESETS,
        default=None,
        required=False,
        help="Presets for common patterns",
    )

    return parser.parse_args()


# Example usage:
if __name__ == "__main__":
    args = parse_args()
    result = main(args.PATTERN, args.replace, args.preset)
    clipboard.copy(result)
    print(result)
    sys.exit()
