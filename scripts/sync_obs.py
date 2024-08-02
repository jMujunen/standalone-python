#!/usr/bin/env python3
"""This script mounts the windows ssd, compresses the OBS clips by outputting to local storage"""

import os

from Color import cprint, style
from fsutils import FileManager, Video
from ProgressBar import ProgressBar
from size import Converter

FOLDERS = {
    "PLAYERUNKNOWN'S BATTLEGROUNDS": "PUBG",
}

OUTPUT_PATH = "/mnt/ssd/OBS/Joona"
INPUT_PATH = "/mnt/win_ssd/Users/Joona/Videos/NVIDIA/"


def main(input_dir: str, output_dir: str) -> None:
    """Compress videos specified by input FileManager and save them to  output FileManager.

    This script iterates over all directories in the input path,
    compresses video files found within those directories,
    and saves the compressed versions to the output directory.

    Once compressed, it removes the original
    Compression is successful and the file is not corrupt.

    Prints the total amount of space saved from the compression process

    Paramters:
    ---------
        input_dir (str): The path to the directory containing the videos to be compressed.
        output_dir (str): The path where the compressed video files will be saved.

    """
    path = FileManager(input_dir)
    SIZE_BEFORE = 0
    SIZE_AFTER = 0
    # Iterate over all directories in path, compressing videos
    # and removing original files if compression was successful.
    with ProgressBar(len(path.videos)) as p:
        for directory in path.dirs:
            if isinstance(directory, FileManager):
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
