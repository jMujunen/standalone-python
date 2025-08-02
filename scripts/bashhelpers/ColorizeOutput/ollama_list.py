#!/usr/bin/env python3
"""Colorize the output of the `ollama list` command."""

from Color import fg, style
from Styler import Styler


def main(*args) -> str:
    """Colorize the output of the `ollama list` command.

    Args:
    -----
        *args (Any): Additional arguments to pass to the subprocess when running the command

    Returns:
    --------
        - sorted output (str): The final, sorted result to print
    """
    llama = Styler("ollama", "list", *args)

    # Size column
    llama.body_style(r"(\w+[-\._]?\w*[-\._]?\w*:[^\s]+)", style.bold)
    llama.body_style(r"([1-4]\.\d+) GB", fg.green)
    llama.body_style(r"([5-6]\.\d+) GB", fg.yellow)
    llama.body_style(r"([7-9]\.\d+|\d{2} GB)", fg.red)
    llama.body_style(r"(\d+ MB)", style.bold)
    # Name column
    llama.body_style(r"([^\s]*[Ll]lama[^\s]*:)", fg.magenta)
    llama.body_style(
        r"([^\s]*[Ll]ava[^\s]*|[^\s]*minicpm[^\s]+|qwen\d?\.?\d+vl):", fg.cyan
    )
    llama.body_style(r"([^\s]*[Cc]ode[^\s]*:)", fg.orange)
    # ])

    llama.remove_by_regex(r"\s([a-z0-9]{12}|ID\s{10})\s")
    return llama.sort()


if __name__ == "__main__":
    import sys

    args = sys.argv[1:]
    print(main(*args))
