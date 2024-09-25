#!/usr/bin/env python3
""" "df.py - Colorize the output of df."""

from Color import fg, style
from Styler import Styler


def main(*args) -> str:
    arguments = ["-h"] if not args else [*args]
    df = Styler("df", *arguments)
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
    return df.sort()


if __name__ == "__main__":
    import sys

    args = sys.argv[1:]
    print(main(*args))
