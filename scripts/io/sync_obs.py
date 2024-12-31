#!/usr/bin/env python3
"""Runs momentis on all clips in the path, shows the results."""

from pathlib import Path

import momentis.momentis
import momentis.utils
from Color import cprint
from fsutils.dir import Dir, obj
from fsutils.video import Video
from fsutils.utils.Exceptions import CorruptMediaError
import os
from ProgressBar import ProgressBar

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


class TempDir:
    """Context manager for temporary directory."""

    def __init__(self, path: str) -> None:
        self.path = Path(path)

    def __enter__(self):
        self.path.mkdir(parents=True, exist_ok=True)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for root, dirs, _ in os.walk(self.path, topdown=False):
            for d in dirs:
                os.rmdir(os.path.join(root, d))
        os.rmdir(self.path)


class Compress:
    """Context manager to ensure a file is successfully compressed before removal."""

    def __init__(self, compressed: str | Path) -> None:
        self.compressed_path = compressed

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.compressed_vid = Video(str(self.compressed_path))
        if any((self.compressed_vid.is_corrupt, self.compressed_vid.size < 300)):
            Path(self.compressed_vid.path).unlink()
            raise CorruptMediaError("Corrupt media detected.", self.compressed_vid.path)
        print("\033[31mRemoving", self.compressed_vid.path, end="\033[0m\n")
        Path(self.compressed_vid.path).unlink()


def main(input_dir: str, output_dir: str) -> list[Video]:
    """Compress videos specified by input Dir and save them to output Dir."""
    tmp_path = "./.momentis_tmp"

    compressed: list[Video] = []

    with TempDir(tmp_path):
        # Run momentis on the input directory
        temp_dir = Dir(tmp_path)
        momentis.momentis.main(
            input_path=input_dir,
            keywords=KEYWORDS,
            debug=False,
            output_path=tmp_path,
        )
        with ProgressBar(len(list(temp_dir.videos()))) as pb:
            for vid in temp_dir.videos():
                try:
                    # Check for videos where no frames got written
                    if vid.size < NULLSIZE:
                        vid.unlink()
                        cprint.debug(f"No frames in {vid.name}. Removed...")
                        continue
                    # Transcode video
                    video_output_path = Path(output_dir, vid.name)
                    with Compress(vid.path):
                        compressed.append(vid.compress(output=video_output_path))

                except KeyboardInterrupt:
                    break
                pb.increment()
    return compressed


if __name__ == "__main__":
    # results = main(INPUT_PATH, OUTPUT_PATH)
    results = main(INPUT_PATH, OUTPUT_PATH)
    print("Results")
    print("\n".join([f"{(vid.name, len(vid))}" for vid in results]))
