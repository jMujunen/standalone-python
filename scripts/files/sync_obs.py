#!/usr/bin/env python3
"""Runs momentis on all clips in the path, removes originals after."""

import os
from pathlib import Path

from Color import cprint, fg, style
from fsutils import Dir, Video
from momentis import (
    KEYWORDS,
    main as momentis,
)
from ProgressBar import ProgressBar
from size import Size

FOLDERS = {
    "PLAYERUNKNOWN'S BATTLEGROUNDS": "PUBG",
}

OUTPUT_PATH = "/mnt/ssd/OBS/Joona"
INPUT_PATH = "/mnt/win_ssd/Users/Joona/Videos/NVIDIA/"
HOFFMAN = KEYWORDS["hoff"]


def main(
    input_path: str = INPUT_PATH, output_path: str = OUTPUT_PATH, keywords: list = HOFFMAN
) -> None:
    """Compress videos specified by input Dir and save them to output Dir."""
    input_dir = Dir(input_path)

    momentis(input_path=input_path, keywords=keywords, debug=False)
    processsed_dir = Dir(Path(input_path, "opencv-output"))

    output_dir = Dir(output_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    if processsed_dir.exists():
        for vid in processsed_dir.videos:
            # Check for videos where no frames got written
            if int(vid.size) < 300:
                vid.unlink()
                cprint.debug(f"No frames in {vid.name}. Removed...")
                continue
            if vid.name.removeprefix("cv2_") in input_dir.content:
                original_video = input_dir.search(vid.name.removeprefix("cv2_"))
                if original_video:
                    original_video = original_video[0]
                    original_video.unlink()
                    cprint.info(f"{vid.path} processed. Removed original {original_video.path}")
                vid.rename(Path(output_path, vid.name))
                cprint.info(f"Moved {vid.name} to output dir")
    else:
        print("No videos found for processing.")


if __name__ == "__main__":
    main(INPUT_PATH, OUTPUT_PATH)
