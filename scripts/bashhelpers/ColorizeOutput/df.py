#!/usr/bin/env python3
""" "df.py - Colorize the output of df"""

import re


from Styler import Styler
from Color import fg, style

df = Styler("df -h")
df.remove_by_row("credentials")
df.remove_by_row("efivars")
df.colorized_command_output(
    [
        df.body_style(r"^([^\s]+.*)\n", style.bold),
        df.body_style(r"(/dev/[ns][vd]\w+)", fg.cyan),
        df.body_style(r"(tmpfs)", fg.yellow),
        df.body_style(r"([8-9]\d%)", fg.red),
        df.body_style(r"[6-7]\d%", fg.orange),
        df.body_style(r"tmpfs.*(\s\d{2}%)", fg.deeppink),
        df.body_style(r"tmpfs.*(\s[2-9]%)", fg.yellow),
        df.body_style(r"(/boot|/home|\s/\s)", fg.green),
        df.body_style(r"(\d{2}\.\d\.\d\.\d{2,3}:/\w+/?\w+?)", fg.blue),  # 10.0.0.50:/hdd")
    ]
)

print(df.sort())
