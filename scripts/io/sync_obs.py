#!/usr/bin/env python3
"""Runs momentis on all clips in the path, shows the results."""

import argparse

import momentis.momentis

FOLDERS = {
    "PLAYERUNKNOWN'S BATTLEGROUNDS": "PUBG",
}

OUTPUT_PATH = "/mnt/ssd/OBS/Joona/opencv-output"
INPUT_PATH = "/mnt/win_ssd/Users/Joona/Videos/NVIDIA/PLAYERUNKNOWN'S BATTLEGROUNDS"

NULLSIZE = 300

KEYWORDS = momentis.utils.parse_keywords()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    momentis.momentis.main(
        input_path=INPUT_PATH,
        keywords=KEYWORDS,
        debug=args.debug,
        output_path=OUTPUT_PATH,
    )
