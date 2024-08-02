#!/usr/bin/env python3
"""Parse data structures from arbitrary text"""

import ast
import os
import sys


# Define a function to recursively parse lists within square brackets
def find_lists(text: str) -> list:
    """Parses and extracts nested lists from a given string using Python's ast module.

    Example:
    -------
        >>> find_lists("[1, 2, [3, 4], {5: 'a'}]")
            [[1, 2, [3, 4], {5: 'a'}]]

        >>> find_lists("This is a test without any lists.")
            []
    """
    stack = []
    lists = []
    i = 0
    while i < len(text):
        if text[i] == "[":
            # Start of a list, push the current position onto the stack
            stack.append(i)
        elif text[i] == "]" and stack:
            # End of a list, pop from the stack and check if we need to parse this list
            start = stack.pop()
            inner_content = text[start + 1 : i].strip()  # Extract content inside brackets
            if inner_content:
                try:
                    parsed_list = ast.literal_eval("[" + inner_content + "]")
                    lists.append(parsed_list)
                except (ValueError, SyntaxError):
                    print("Could not parse list at position", start)
        i += 1
    return lists[-1]


def main(file: str) -> list | None:
    if os.path.exists(file):
        with open(file) as f:
            content = f.read()
        return find_lists(content)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 parse_data_structures.py <filename>")
    else:
        result = main(sys.argv[1])
        if result is not None:
            for item in result:
                if isinstance(item, list):
                    print("\n".join(item))
                print("=" * 60)
