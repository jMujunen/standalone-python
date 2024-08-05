#!/usr/bin/env python3
"""This script mounts the windows ssd, compresses the OBS clips by outputting to local storage"""

import os

from Color import cprint, style
from fsutils import Dir, Video
from ProgressBar import ProgressBar
from size import Converter

FOLDERS = {
    "PLAYERUNKNOWN'S BATTLEGROUNDS": "PUBG",
}

OUTPUT_PATH = "/mnt/ssd/OBS/Joona"
INPUT_PATH = "/mnt/win_ssd/Users/Joona/Videos/NVIDIA/"


def main(input_dir: str, output_dir: str) -> None:
    """Compress videos specified by input Dir and save them to output Dir.

    Once compressed, it removes the original.
    """
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
                if not os.path.exists(output_folder):
                    os.makedirs(output_dir, exist_ok=True)
                for vid in directory.videos:
                    p.increment()
                    output_path = os.path.join(output_folder, vid.basename)
                    SIZE_BEFORE += vid.size
                    vid.compress(output=output_path)
                    new_video_object = Video(output_path)
                    SIZE_AFTER += new_video_object.size
                    if not new_video_object.is_corrupt:
                        os.remove(vid.path)
    cprint(f"Space saved: {Converter(SIZE_BEFORE - SIZE_AFTER)}", style.bold)


if __name__ == "__main__":
    main(INPUT_PATH, OUTPUT_PATH)
