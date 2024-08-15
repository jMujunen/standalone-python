#!/usr/bin/env python3
"""This script mounts the windows ssd, compresses the OBS clips by outputting to local storage"""

import os

from Color import cprint, fg, style
from ProgressBar import ProgressBar
from size import Converter

from fsutils import Dir

# CMD = ffmpeg -hwaccel cuda -i input.mp4 -c:v libx265 -preset veryslow -tune hq -x265-params "lossless=1"


FOLDERS = {
    "PLAYERUNKNOWN'S BATTLEGROUNDS": "PUBG",
}

OUTPUT_PATH = "/mnt/ssd/OBS/Joona"
INPUT_PATH = "/mnt/win_ssd/Users/Joona/Videos/NVIDIA/"
# [ ] : Implement LOGS_INPUT_PATH = "/mnt/win_ssd/Users/Joona/Documents/Logs"
# [ ] :  LOGS_OUTPUT_PATH = "/home/joona/Logs"


# @staticmethod
# def log_sync():
#     """Sync the hwmonitoring logs"""
#     logs = Dir(LOGS_INPUT_PATH).file_objaects


def main(input_dir: str, output_dir: str) -> None:
    """Compress videos specified by input Dir and save them to output Dir."""
    path = Dir(input_dir)
    SIZE_BEFORE = 0
    SIZE_AFTER = 0
    # Iterate over all directories in path, compressing videos
    # and removing original files if compression was successful.
    with ProgressBar(len(path.videos)) as p:
        for directory in path.dirs:
            if isinstance(directory, Dir):
                if directory.is_empty:
                    continue
                # Modify the name of the folder to match the spec
                output_folder = os.path.join(
                    output_dir, FOLDERS.get(directory.basename, directory.basename)
                )
                os.makedirs(output_folder, exist_ok=True)
                for vid in directory.videos:
                    p.increment()
                    try:
                        output_path = os.path.join(output_folder, vid.basename)
                        compressed = vid.compress(output=output_path)
                        SIZE_BEFORE += vid.size
                        SIZE_AFTER += compressed.size
                        if compressed.exists and not compressed.is_corrupt:
                            os.remove(vid.path)

                    except Exception as e:
                        cprint(f"Error compressing video {vid.basename}: {e}", fg.orange)
    cprint(f"Space saved: {Converter(SIZE_BEFORE - SIZE_AFTER)}", style.bold)


if __name__ == "__main__":
    main(INPUT_PATH, OUTPUT_PATH)
