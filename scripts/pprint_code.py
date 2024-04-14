#!/usr/bin/env python3

# pprint_code.py - Formats and copies code to the clipboard

import sys
import pyperclip

def format_code(code, language):
    # TODO Implement formatting logic for each language
    if language == "html":
        # TODO Format HTML code
        pass
    elif language == "css":
        # TODO Format CSS code
        pass
    elif language == "javascript":
        # TODO Format JavaScript code
        pass
    else:
        # TODO Default formatting for unknown languages
        pass

    return formatted_code

def main():
    # Get the code from the user's clipboard
    code = pyperclip.paste()

    # Get the language from the command line arguments
    language = sys.argv[1]

    # Format the code
    formatted_code = format_code(code, language)

    # Output the formatted code to the user's clipboard
    pyperclip.copy(formatted_code)

if __name__ == "__main__":
    main()