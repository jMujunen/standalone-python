#!/usr/bin/env python3
"""lsblk.py - Colorize the output of lsblk."""

import subprocess
import sys

from Styler import Styler


def main(*args) -> str:
    arguments = ["-o", "NAME,FSTYPE,LABEL,UUID,FSUSE%"] if not args else [*args]
    print(arguments)
    lsblk_styler = Styler("lsblk", *arguments)
    style_rules = [
        # Match device names
        lsblk_styler.body_style(r"(sd[a-z][^0-9]|nvme[0-9]n[0-9][^a-z0-9])", "33"),
        # Match Partitions
        lsblk_styler.body_style(
            r"(sd[a-z][0-9]|nvme[0-9]n[0-9][a-z0-9]+)", "38;2;93;163;209"
        ),
        # Match digit percentages
        # Color by value
        lsblk_styler.body_style(r"(.?\d+%)", "32"),
        lsblk_styler.body_style(r"([8-9]\d%)", "31"),
        lsblk_styler.body_style(r"[6-7]\d%", 33),
        # # Match header
        lsblk_styler.body_style(r"^([^\s]+.*)\n", "2;38;2;255;255;255"),
    ]

    return lsblk_styler.colorized_command_output(style_rules)


if __name__ == "__main__":
    args = sys.argv[1:]

    print(main(*args))
    # main()
