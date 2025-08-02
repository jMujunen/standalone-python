#!/usr/bin/env python3
"""lsblk.py - Colorize the output of lsblk."""

import sys

from Styler import Styler


def main(*args) -> str:
    lsblk = Styler("lsblk", "-o", "NAME,FSTYPE,LABEL,UUID,FSUSE%", *args)

    # Match device names
    lsblk.body_style(r"(sd[a-z][^0-9]|nvme[0-9]n[0-9][^a-z0-9])", "33")
    # Match Partitions
    lsblk.body_style(r"(sd[a-z][0-9]|nvme[0-9]n[0-9][a-z0-9]+)", "38;2;93;163;209")
    # Match digit percentages
    # Color by value
    lsblk.body_style(r"(.?\d+%)", "32")
    lsblk.body_style(r"([8-9]\d%)", "31")
    lsblk.body_style(r"[6-7]\d%", 33)
    # # Match header
    lsblk.body_style(r"^([^\s]+.*)\n", "2;38;2;255;255;255")

    return str(lsblk)


if __name__ == "__main__":
    args = sys.argv[1:]

    print(main(*args))
    # main()
