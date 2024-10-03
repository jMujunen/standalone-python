#!/usr/bin/env python3
"""df.py - Colorize the output of df."""

from Color import fg, style
from Styler import Styler


def main(*args) -> str:
    arguments = ["--human-readable", "--no-sync"] if not args else [*args]

    df = Styler("df", *arguments)

    # Remove undesired rows
    df.remove_by_row("credentials")
    df.remove_by_row("overlay")

    # Colorize and styling the command output based on regular expressions
    df.colorized_command_output(
        [
            # Bold the header line
            df.body_style(r"^([^\s]+.*)\n", style.bold),
            df.body_style(r"(/dev/[ns][vd]\w+)", fg.cyan),
            # Highlighting 'tmpfs' partitions in yellow
            df.body_style(r"(tmpfs)", fg.yellow),
            # Highlighting used space above 80% in red
            df.body_style(r"([8-9]\d%)", fg.red),
            # Highlighting used space between 60% and 79% in orange
            df.body_style(r"[6-7]\d%", fg.orange),
            # Highlighting 'tmpfs' partitions with usage above 20% in deep pink
            df.body_style(r"tmpfs.*(\s\d{2}%)", fg.deeppink),
            # Highlighting 'tmpfs' partitions with usage between 10% and 19% in yellow
            df.body_style(r"tmpfs.*(\s[2-9]%)", fg.yellow),
            # Highlighting '/boot', '/home' and blank lines in green
            df.body_style(r"(/boot|/home|\s/\s)", fg.green),
            # Highlighting IP addresses and mount points in blue (e.g., 10.0.0.50:/hdd)
            df.body_style(r"(\d{2}\.\d.\d.\d{2,3}:/\w+/?\w*?)", fg.blue),
        ]
    )

    return df.sort()


if __name__ == "__main__":
    import sys

    args = sys.argv[1:]
    print(main(*args))
