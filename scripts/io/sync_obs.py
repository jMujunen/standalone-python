#!/usr/bin/env python3
"""Runs momentis on all clips in the path, removes originals after."""

from pathlib import Path

import momentis.momentis
import momentis.utils
from Color import cprint
from fsutils.dir import Dir, Video, obj

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


def main(input_path: Dir, output_path: Dir) -> list[Video]:
    """Compress videos specified by input Dir and save them to output Dir."""
    input_dir = Dir(input_path)

    momentis.momentis.main(
        input_path=input_path,
        keywords=KEYWORDS,
        debug=False,
        output_path=output_path,
    )

    processed_dir = Dir(Path(input_path, "opencv-output"))
    Path(OUTPUT_PATH).mkdir(parents=True, exist_ok=True)

    if processed_dir.exists():
        for vid in processed_dir.videos:
            # Check for videos where no frames got written
            if vid.size < NULLSIZE:
                vid.unlink()
                cprint.debug(f"No frames in {vid.name}. Removed...")
                continue

    else:
        print("No videos found for processing.")
        return []
    return Dir(OUTPUT_PATH).videos


if __name__ == "__main__":
    import sys

    input_dir = Dir(INPUT_PATH)
    output_dir = Dir(OUTPUT_PATH)

    results = main(INPUT_PATH, OUTPUT_PATH)
    if len(sys.argv) > 1 and sys.argv[1] == "--remove" and results:
        for processed_vid in results:
            if processed_vid.name.removeprefix("cv2_") in input_dir.content:
                original_video = obj(
                    input_dir.content.pop(
                        input_dir.content.index(processed_vid.name.removeprefix("cv2_"))
                    )
                )
                if original_video:
                    original_video.unlink()
                    cprint.info(
                        f"{processed_vid.path} processed. Removed original {original_video.path}"
                    )
    else:
        print("Results")
        print("\n".join([f"{(vid.name, len(vid))}" for vid in results]))
