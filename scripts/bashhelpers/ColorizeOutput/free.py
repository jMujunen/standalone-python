#!/usr/bin/env python3
"""free.py - Colorized wrapper for gnu 'free -h'"""

import argparse
import subprocess

from Color import fg, style
from Styler import Styler


def parse_data() -> str:
    r"""Parse the output from `free | grep "Mem\|Swap"`"""
    command_output = subprocess.run(
        'free | grep -oP "(Mem|Swap):.*"', shell=True, capture_output=True, text=True, check=False
    ).stdout.strip()
    mem, swap = command_output.split("\n")
    mem_total, mem_used, mem_free, mem_shared, cached, mem_avail = mem.split()[1:]
    swap_total, swap_used, swap_free = swap.split()[1:]

    # Mem used is calculation:
    # 100 minus ratio of free to total memory multiplied by 100.
    # 100 - free/total * 100
    mem_used_percent = f"{(abs(round((float(mem_free) / float(mem_total)) * 100 - 100, 1)))}%"

    # Same calculation as mem used. If there's no swap (i.e., it's zero) set it as N/A
    try:
        swap_used_percent = (
            f"{(abs(round((float(swap_free) / float(swap_total)) * 100 - 100, 1)))}%"
        )
    except ZeroDivisionError:
        swap_used_percent = "N/A"

    # cached / total memory * 100.
    cached_percent = f"{(round((float(cached) / float(mem_total)) * 100, 1))}%"

    return f"""{" ".ljust(10)}{"Used".ljust(10)}{"Cached".ljust(10)}
{"Mem:".ljust(10)}{mem_used_percent.ljust(10)}{cached_percent.ljust(10)}
{"Swap:".ljust(10)}{swap_used_percent.ljust(10)}"""


"          Used      Cached    \nMem:      97.2%     63.3%     \nSwap:     27.0%     "


def main(*args) -> None:
    free = Styler(parse_data())
    free.colorized_command_output(
        [
            # Mem used
            free.body_style(r"(?<=Mem:......)([1-4]\d\.\d%)", fg.green),  # 10-40%
            free.body_style(r"(?<=Mem:......)([5-7]\d\.\d%)", fg.yellow),  # 50-70%
            free.body_style(r"(?<=Mem:......)([8-9]\d\.\d%)", fg.red),  # 80-90%
            # Mem cached
            free.body_style(r"[^\s:]\s{5}([(1-3]\d\.\d%)", fg.red),  # 10-30%
            free.body_style(r"[^\s:]\s{5}([4-6]\d\.\d%)", fg.yellow),  # 40-60%
            free.body_style(r"[^\s:]\s{5}([6-9]\d\.\d%)", fg.green),  # 60-90%
            # Swap
            free.body_style(r"(?<=Swap:.....)([2-5]\d\.\d%)", fg.yellow),  # 30-50%
            free.body_style(r"(?<=Swap:.....)([5-9]\d\.\d%)", fg.red),  # 50-90%
            free.body_style(r"(?<=Swap:.....)(100.\d?%)", fg.red),
            # Header
            free.body_style(r"^([\s]+.*)\n", style.bold),
        ]
    )

    print(free.sort())


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="df wrapper")
    parser.add_argument(
        "--human-readable",
        "-H",
        action="store_true",
        help="Print sizes in human readable format (e.g., 1K 234M 2G)",
    )
    parser.add_argument("--watch", "-w", action="store_true", help="Watch continuously")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    main(*vars(args).values())

