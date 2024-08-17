#!/usr/bin/env python3
"""free.py - Colorized wrapper for gnu 'free -h'"""

import subprocess

from Color import fg, style
from Styler import Styler

command_output = subprocess.run(
    'free | grep -oP "(Mem|Swap):.*"', shell=True, capture_output=True, text=True, check=False
).stdout

mem = command_output.split("\n")[0]
swap = command_output.split("\n")[1]

mem_total = mem.split()[1]
mem_used = mem.split()[2]
mem_free = mem.split()[3]

cached = mem.split()[5]

swap_total = swap.split()[1]
swap_used = swap.split()[2]
swap_free = swap.split()[3]

mem_used_percent = f"{(abs(round((float(mem_free) / float(mem_total)) * 100 - 100, 1)))}%"
try:
    swap_used_percent = f"{(abs(round((float(swap_free) / float(swap_total)) * 100 - 100, 1)))}%"
except ZeroDivisionError:
    swap_used_percent = "N/A"

cached_percent = f"{(round((float(cached) / float(mem_total)) * 100, 1))}%"

text = f"""{" ".ljust(10)}{"Used".ljust(10)}{"Cached".ljust(10)}
{"Mem:".ljust(10)}{mem_used_percent.ljust(10)}{cached_percent.ljust(10)}
{"Swap:".ljust(10)}{swap_used_percent.ljust(10)}"""

free = Styler(text)

free.colorized_command_output(
    [
        free.body_style(r"([1-4]\d\.\d%)", fg.green),
        free.body_style(r"([5-7]\d\.\d%)", fg.yellow),
        free.body_style(r"([8-9]\d\.\d%)", fg.red),
        free.body_style(r"^([\s]+.*)\n", style.bold),
    ]
)

print(free.sort())
