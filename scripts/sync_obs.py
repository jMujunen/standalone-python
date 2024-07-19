#!/usr/bin/env python3
"""This script mounts the windows ssd, compresses the OBS clips by outputting to local storage"""

import os

from size import Converter
from fsutils import Video, Dir
from Color import cprint, style
from ProgressBar import ProgressBar

FOLDERS = {
    "PLAYERUNKNOWN'S BATTLEGROUNDS": "PUBG",
}
OUTPUT_PATH = "/mnt/ssd/OBS/Joona"


def main():
    path = Dir("/mnt/win_ssd/Users/Joona/Videos/NVIDIA/")
    size_before = 0
    size_after = 0
    with ProgressBar(len(path.videos)) as p:
        for directory in path.dirs:
            if isinstance(directory, Dir):
                if directory.is_empty:
                    continue
                output_dir = os.path.join(OUTPUT_PATH, directory.basename)
                if directory.basename in FOLDERS:
                    output_dir = os.path.join(
                        "/mnt/ssd/OBS/Joona", FOLDERS[directory.basename]
                    )

                if not os.path.exists(output_dir):
                    os.makedirs(output_dir, exist_ok=True)
                for vid in directory.videos:
                    p.increment()
                    size_before += vid.size
                    vid.compress(output_dir)
                    new = Video(os.path.join(output_dir, vid.basename))
                    size_after += new.size
                    if not new.is_corrupt:
                        os.remove(vid.path)
    cprint(f"Space saved: {Converter(size_before - size_after)}", style.bold)


if __name__ == "__main__":
    main()
