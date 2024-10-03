#!/usr/bin/env python3

from Color import fg, style
from Styler import Styler


def main(*args) -> str:
    """Colorize the output of the `ollama list` command.

    Args:
    -----
        - any [Any]: Additional arguments to pass to the subprocess when running the command

    Returns:
    --------
        - sorted output (str): The final, sorted result to print
    """
    arguments = [*args] if args else ["list"]
    print(arguments)
    llama = Styler("ollama", *arguments)

    llama.colorized_command_output(
        [
            llama.body_style(r"(\w+[-\._]?\w*[-\._]?\w*:[^\s]+)", style.bold),
            llama.body_style(r"([1-4]\.\d+) GB", fg.green),
            llama.body_style(r"([5-6]\.\d+) GB", fg.yellow),
            llama.body_style(r"([7-9]\.\d+|\d{2} GB)", fg.red),
            llama.body_style(r"(\d+ MB)", style.bold),
        ]
    )
    llama.remove_by_regex(r"\s([a-z0-9]{12}|ID\s{10})\s")
    return llama.sort()


if __name__ == "__main__":
    import sys

    args = sys.argv[1:]
    print(main(*args))
