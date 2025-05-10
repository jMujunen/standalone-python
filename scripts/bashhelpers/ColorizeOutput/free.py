#!/usr/bin/env python3
"""free.py - Colorized wrapper for gnu 'free -h'."""

import argparse
import os
import subprocess
from sys import platform
from time import sleep

from Color import fg, style
from Styler import Styler


def parse_data() -> str:
    r"""Parse the output from `free | grep "Mem\|Swap"`."""
    command_output = subprocess.run(
        'free | grep -oP "(Mem|Swap):.*"',
        shell=True,
        capture_output=True,
        text=True,
        check=False,
    ).stdout.strip()
    mem, swap = command_output.split("\n")
    mem_total, mem_used, mem_free, mem_shared, cached, mem_avail = mem.split()[1:]
    swap_total, swap_used, swap_free = swap.split()[1:]

    # Mem used is calculation:
    # 100 minus ratio of free to total memory multiplied by 100.
    # 100 - free/total * 100
    mem_used_percent = (
        f"{(abs(round((float(mem_free) / float(mem_total)) * 100 - 100, 1)))}%"
    )

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


def colorize() -> str:
    """Colorizes the text based on usage."""
    free = Styler(parse_data(), skip_subprocess=True)
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
    return free.sort()


def clear() -> None:
    os.system("clear") if platform == "linux" else os.system("cls")


def watch(interval: float | int) -> int:
    while True:
        try:
            clear()
            print(colorize())
            sleep(interval)
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print("Error occurred:\n", str(e))
            return 1
    return 0


def main(watch_flag: bool, watch_interval: float | int) -> str | int:
    if watch_flag:
        return watch(watch_interval)
    print(colorize())
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="df wrapper")
    parser.add_argument(
        "--watch", "-w", action="store_true", help="Watch continuously", default=False
    )
    parser.add_argument("--interval", "-i", default=2, help="Watch interval in seconds")
    parser.add_argument(
        "args",
        nargs=argparse.REMAINDER,
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    main(args.watch, args.interval)
