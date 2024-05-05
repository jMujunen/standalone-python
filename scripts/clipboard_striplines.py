#!/usr/bin/env python3

# clipboard_striplines.py - strips a character from each line,
# using the clipboard as I/O source

import pyperclip
import argparse


def parse_args():
    parser = argparse.ArgumentParser(
        description='Strips a character from each line, using the clipboard as I/O source',
    )

    parser.add_argument('char', type=str, help='Character to strip')
    parser.add_argument('-r', '--replace',
                        help='Replace character with this instead of stripping')
    return parser.parse_args()


def main(char):
    try:
        text = pyperclip.paste()
        lines = text.split('\n')
        for i in range(len(lines)):
            lines[i] = lines[i].replace(char, '')
        text = '\n'.join(lines)
        pyperclip.copy(text)
        print(text)
        return 0
    except Exception as e:
        print(e)
        return 1


if __name__ == '__main__':
    args = parse_args()
    main(args.char)
