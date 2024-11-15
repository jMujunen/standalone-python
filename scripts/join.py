#!/usr/bin/env python3
"""Turns a multiline string to a single line
Function to replace newline characters with a space and copy the result to clipboard.

Parameters
    text (str): The multiline string to be converted.

Returns
    str: The single line string.
"""

import clipboard


def main(text):
    out = text.replace("\n", " ")
    clipboard.copy(out)
    return out


if __name__ == "__main__":
    text = clipboard.paste()
    print(main(text))
