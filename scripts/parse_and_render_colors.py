#!/usr/bin/env python3

from pathlib import Path
import clipboard

import json

from Color import Color, color_names, fg


def main(path: str | Path) -> None:
    pallet = json.loads(Path(path).read_text(encoding="utf-8"))
    offwhite = color_names["gray90"]
    darkgray = color_names["gray10"]
    colors = [Color.from_hex(color) for color in pallet]

    for color in colors:
        for step in color.fade(start=offwhite, end=darkgray):
            print(f"{step}▓▓▓▓▓▓", end="\033[0m")
        print()


if __name__ == "__main__":
    main("/home/joona/python/assets/everforest.json")
