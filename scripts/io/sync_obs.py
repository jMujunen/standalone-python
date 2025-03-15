#!/usr/bin/env python3
"""Runs momentis on all clips in the path, shows the results."""

from pathlib import Path

import momentis.momentis
import momentis.utils
from Color import cprint
from fsutils.dir import Dir
from fsutils.video import Video
from fsutils.utils.Exceptions import CorruptMediaError
import os
from ProgressBar import ProgressBar

FOLDERS = {
    "PLAYERUNKNOWN'S BATTLEGROUNDS": "PUBG",
}

OUTPUT_PATH = "/mnt/ssd/OBS/Joona/opencv-output"
INPUT_PATH = "/mnt/win_ssd/Users/Joona/Videos/NVIDIA/PLAYERUNKNOWN'S BATTLEGROUNDS"

KEYWORDS = [
    "sofunny",
    "meso",
    "solunny",
    "hoff",
    "ffman",
    "bartard",
    "dankniss",
    "vermeme",
    "nissev",
    "you",
]
NULLSIZE = 300


if __name__ == "__main__":
    momentis.momentis.main(
        input_path=INPUT_PATH, keywords=KEYWORDS, debug=False, output_path=OUTPUT_PATH
    )
