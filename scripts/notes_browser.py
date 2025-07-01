#!/usr/bin/env python3
import os
import subprocess
from typing import SupportsRound

from rich import theme
from rich.console import Console
from rich.markdown import Markdown

# LOCATION = "/home/joona/Docs/Exported Markdown/HTML"
LOCATION = "/home/joona/Docs/Notes/Obsidian/All Notes/"


def get_html_files(location: str) -> list[str]:
    results = []
    for root, _, files in os.walk(LOCATION):
        for file in files:
            if file.endswith(".md"):
                results.append(os.path.relpath(os.path.join(root, file), LOCATION))  # noqa PERF401
    return results


def main() -> int:
    console = Console(width=120)
    files = get_html_files(LOCATION)

    choice = subprocess.run(
        ["wofi", "--show", "dmenu"],
        input="\n".join(files),
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    print(choice)
    with open(os.path.join(LOCATION, choice)) as f:
        content = f.read()
    res = subprocess.Popen(
        [
            "kitty",
            "-T",
            choice,
            "--hold",
            "python3",
            "-m",
            "rich.markdown",
            "--code-theme",
            "material",
            "-i",
            "bash",
            "--width",
            "100",
            os.path.join(LOCATION, choice),
        ],
    )
    print(res)
    return 1
    console.print(
        Markdown(
            content,
            code_theme="material",
            inline_code_lexer="bash",
            inline_code_theme="monokai",
        )
    )
    return 0
    # subprocess.Popen(["firefox", os.path.join(LOCATION, choice)])


if __name__ == "__main__":
    import sys

    main()
