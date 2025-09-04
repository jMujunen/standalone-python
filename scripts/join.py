#!/usr/bin/env python3
"""Turn a multiline string to a single line."""

import clipboard


def main(text):
    out = text.replace("\n", " ")
    clipboard.copy(out)
    return out


if __name__ == "__main__":
    text = clipboard.paste()
    print(main(text))
