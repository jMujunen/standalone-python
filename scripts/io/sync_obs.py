#!/usr/bin/env python3
"""Runs momentis on all clips in the path, shows the results."""

from pathlib import Path

import momentis.momentis
import momentis.utils
from Color import cprint
from fsutils.dir import Dir, obj
from fsutils.video import Video

FOLDERS = {
    "PLAYERUNKNOWN'S BATTLEGROUNDS": "PUBG",
}

OUTPUT_PATH = "/mnt/ssd/OBS/Joona/opencv-output"
INPUT_PATH = "/mnt/win_ssd/Users/Joona/Videos/NVIDIA/"
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


def main(inputDir: Dir, outputDir: Dir) -> list[Video]:
    """Compress videos specified by input Dir and save them to output Dir."""

    momentis.momentis.main(
        input_path=inputDir,
        keywords=KEYWORDS,
        debug=False,
        output_path=outputDir.path,
    )
    processed_dir = Dir(Path(inputDir, "opencv-output"))
    Path(OUTPUT_PATH).mkdir(parents=True, exist_ok=True)
    if processed_dir.exists():
        for vid in processed_dir.videos:
            # Check for videos where no frames got written
            if vid.size < NULLSIZE:
                vid.unlink()
                cprint.debug(f"No frames in {vid.name}. Removed...")
                continue

    return Dir(OUTPUT_PATH).videos


def remove_flagged(flagged: list[Video]) -> None:
    """Remove flagged videos from the input directory."""
    for video in flagged:
        if video.name.startswith("cv2_"):
            original_path = Path(input_dir.path, video.name.removeprefix("cv2_"))
            if original_path.exists():
                original_path.unlink()
                cprint.info(f"Removed original {original_path}")
            else:
                cprint.warn(f"Original {original_path} not found.")


if __name__ == "__main__":
    import sys

    results = main(Dir(INPUT_PATH), Dir(OUTPUT_PATH))
    if len(sys.argv) > 1 and sys.argv[1] == "--remove" and results:
        remove_flagged(results)
    else:
        print("Results")

        print("\n".join([f"{(vid.name, len(vid))}" for vid in results]))
