#!/usr/bin/env python3
"""This script mounts the windows ssd, compresses the OBS clips by outputting to local storage"""

import os

from Color import cprint, fg, style
from fsutils import Dir
from ProgressBar import ProgressBar
from size import Converter

# CMD = ffmpeg -hwaccel cuda -i input.mp4 -c:v libx265 -preset veryslow -tune hq -x265-params "lossless=1"


FOLDERS = {
    "PLAYERUNKNOWN'S BATTLEGROUNDS": "PUBG",
}

OUTPUT_PATH = "/mnt/ssd/OBS/Joona"
INPUT_PATH = "/mnt/win_ssd/Users/Joona/Videos/NVIDIA/"
LOGS_INPUT_PATH = "/mnt/win_ssd/Users/Joona/Documents"
LOGS_OUTPUT_PATH = "/home/joona/Logs/win_hwlogs"


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
                outdir = Dir(output_folder)
                for vid in directory.videos:
                    # if vid in outdir:
                    #     cprint(
                    #         f"Skipping {vid.basename} because it already exists in the destination."
                    #     )
                    #     continue
                    p.increment()
                    try:
                        output_path = os.path.join(output_folder, f"_{vid.basename}")
                        compressed = vid.compress(output=output_path)
                    except Exception as e:
                        cprint(f"Error compressing video {vid.basename}: {e!r}", fg.orange)
                        continue
                    SIZE_BEFORE += vid.size
                    SIZE_AFTER += compressed.size
                    try:
                        size_ratio = (vid.size - compressed.size) / (
                            vid.bitrate - compressed.bitrate
                        )
                        print(
                            f"File size decreased {style.bold}{size_ratio}x{style.reset} more than bitrate"
                        )
                        if compressed.exists and not compressed.is_corrupt:
                            os.remove(vid.path)
                    except Exception as e:
                        cprint(f"Error removing original video {vid.basename}: {e!r}", fg.red)
    cprint(f"Space saved: {Converter(SIZE_BEFORE - SIZE_AFTER)}", style.bold)


if __name__ == "__main__":
    main(INPUT_PATH, OUTPUT_PATH)
