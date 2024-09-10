#!/usr/bin/env python3

from Color import bg, fg, style
from Styler import Styler

llama = Styler("ollama list")
llama.sort()

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

print(llama)
