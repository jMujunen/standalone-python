#!/usr/bin/env python3
"""Strips <pattern> from clipboard"""
# clipboard_striplines.py - strips a character from each line,
# using the clipboard as I/O source

import argparse
import re

import pyperclip

# TODO - add more presets for common patterns
PRESETS = {
    # Concatenate a multiline string into a single line separated a space
    "multiline": lambda x: " ".join(i.strip() for i in x.split("\n")),
    "trailing": None,
    # Remove REPL prompt chars "...:"
    "ipy": lambda x: re.sub(r"\.\.\.:", "", x, flags=re.MULTILINE),
}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Strips a character or string from each line, using the clipboard as I/O",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
        Example 1:
        ---------

        python3 clipboard_striplines.py --preset=multiline

            alsa-card-profiles      |
            ca-certificates-mozilla |
            dict                    |
            filesystem              |
            geoclue                 |
            -----------------------------------------------------------------
                -> alsa-card-profiles ca-certificates-mozilla dict filesystem geoclue
            ------------------------------------------------------------------

        Example 2:
        -----------

        python3 clipboard_striplines.py --pattern=wlan0 --replace=wlan1

        wlan0: authenticate        ->  wlan1: authenticate
        wlan0: send auth to        ->  wlan1: send auth to
        wlan0: authenticated       ->  wlan1: authenticated
        wlan0: associate with      ->  wlan1: associate with
        wlan0: RX AssocResp from   ->  wlan1: RX AssocResp from
        wlan0: associated          ->  wlan1: associated
        """,
    )
    parser.add_argument(
        "-r",
        "--replace",
        help="Replace character with this instead of stripping.",
        default="",
    )
    parser.add_argument(
        "--pattern",
        help="PCRE - Perl compatiable regex patterns to search for",
        default=" ",
    )

    parser.add_argument("--lstrip", help="Only strip from the left", action="store_true")

    parser.add_argument("--rstrip", help="Only strip from the right", action="store_true")
    parser.add_argument("-l", "--list", help="List presets", action="store_true")
    parser.add_argument(
        "-p",
        "--preset",
        choices=["multiline", "ipy"],
        required=False,
        help="""Presets for common patterns:
        Multiline: Turn a multiline string into a single line""",
        default=["multiline"],
        # Example:
        # -----------------
        #  pyside6-tools-wrappers
        #  python-aiosql
        #  python-clipboard
        #  python-imagehash
        #  python-imageio   --> pyside6-tools-wrappers python-aiosql python-clipboard python-imagehash python-imageio
        # TODO: Add presets for other common patterns
    )

    return parser.parse_args()


def main(char, replacement):
    """
    Strips a character from each line in the clipboard content.

    Paramters:
    ---------
        char(str): Character or pattern to strip. Can be any valid PCRE.
        replacement(str): Optional replacement string.
    """
    try:
        pattern = re.compile(char)
        text = pyperclip.paste()
        # Split the text into individual lines
        lines = text.split("\n")
        # Initialize an empty list to hold the processed lines
        output = []
        for line in lines:
            # Strip the character or pattern from each line
            output.append(re.sub(pattern, replacement, line))
        # Join the output list back into a single text string
        text = "\n".join(output)
        # Update the clipboard with the processed text
        pyperclip.copy(text)
        # Print the processed text for debugging purposes
        print(text)
        return 0
    except Exception as e:
        print(e)
        return 1


# Example usage:
if __name__ == "__main__":
    args = parse_args()
    main(args.pattern, args.replace)
