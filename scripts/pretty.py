#!/usr/bin/env python3

# pretty.py - Pretty print various string inputs

import sys
import os
import argparse


LANGS = {
    "plain": lambda x: x,
    "json": lambda x: x,
    "html": lambda x: x,
}

DELIMS = {
    "newline": "\n",
    "space": " ",
    "tab": "\t",
    "none": "",
    "comma": ",",
    "colon": ":",
    "semicolon": ";",
    "pipe": "|",
    "equals": "=",
    "ampersand": "&",
    "asterisk": "*",
    "plus": "+",
    "minus": "-",
    "slash": "/",
    "backslash": "\\",
    "percent": "%",
    "at": "@",
    "hash": "#",
}

OUTPUT_OPTIONS = {
    "stdout": lambda x: sys.stdout.write(x),
    "file": lambda x: open(x, "w").write(x),
    "clipboard": lambda x: os.system(f'echo "{x}" | xclip -selection clipboard'),
}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Pretty print various string inputs",
    )
    parser.add_argument(
        "INPUT",
        type=str,
        nargs="+",
        help="Input string to pretty print",
    )
    parser.add_argument(
        "-d",
        "--delimiter",
        type=str,
        default="none",
        help="""
        Delimiter between strings - defaults to none
            Options:
                newline
                space
                tab
                none
                comma
        """,
        required=False,
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="clipboard",
        help="""
        Output file
            Options:
                stdout
                file
                clipboard
        """,
        required=False,
    )
    parser.add_argument(
        "-f",
        "--format",
        type=str,
        default="plain",
        help="Output format",
        required=False,
    )
    parser.add_argument(
        "-l",
        "--language",
        type=str,
        default="plain",
        help="Code language",
        required=False,
    )

    return parser.parse_args()


def main(args) -> None:
    output_string = ""
    delim = DELIMS.get(args.delimiter, args.delimiter)

    # Replace each delimiter in the input string(s) with a newline
    for s in args.INPUT:
        output_string += s.replace(delim, "\n")

    # Output to specified output format

    if args.output in OUTPUT_OPTIONS:
        OUTPUT_OPTIONS[args.output](output_string)
    else:
        print(output_string)


if __name__ == "__main__":
    args = parse_args()
    main(args)
