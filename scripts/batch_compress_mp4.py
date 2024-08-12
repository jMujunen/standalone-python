#!/usr/bin/env python3
"""Batch process all .mp4 files in a directory."""

import argparse
import logging
import os
import shutil
from time import sleep

from Color import cprint, fg, style
from fsutils import Dir, Video
from ProgressBar import ProgressBar
from size import Converter

RENAME_SPEC = {
    "PLAYERUNKNOWN": "PUBG",
}

# Create a logger that writes to a file named 'batch_compress.log'
logger = logging.getLogger(__name__)
handler = logging.FileHandler("batch_compress.log")
formatter = logging.Formatter("%(asctime)s [%(levelname)s] - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)  # Set the level of the logger to INFO


def parse_arguments() -> argparse.Namespace:
    """Parse args."""
    parser = argparse.ArgumentParser(description="Batch process all .mp4 files in a directory")
    parser.add_argument(
        "INPUT",
        help="Input directory",
    )
    parser.add_argument("OUTPUT", help="Output directory")
    parser.add_argument(
        "-n",
        "--num",
        help="Number of of files to compress in one sitting",
        type=int,
        default=-1,
    )
    parser.add_argument("--keep", help="Keep original file", action="store_true", default=False)
    return parser.parse_args()


def main(input_dir: str, output_dir: str, num: int) -> tuple[list[Video], list[Video], int, int]:
    # List of file objects
    original_files = []
    compressed_files = []

    size_before = 0
    size_after = 0

    videos = Dir(input_dir).videos[:num]
    outdir = Dir(output_dir)

    try:
        # for folder_path in input_dir.rel_directories:
        # Create the output directories if they don't exist
        os.makedirs(outdir.path, exist_ok=True)
    except OSError as e:
        print(f"[\033[31m Error creating output directory '{outdir}': {e} \033[0m]")
        exit(1)

    # Initialize progress bar vars
    number_of_files = len(videos)
    cprint(f"1/{number_of_files}", style.bold, style.underline, end="\n\n")

    with ProgressBar(number_of_files) as progress:
        for vid in videos:
            print("\n")
            cprint(vid.basename, style.bold)
            print(
                f"Original: bitrate={vid.bitrate_human}, size={vid.size_human}, codec={vid.codec}"
            )
            if (
                vid.codec == "hevc"
                and vid.bitrate < 30000000
                or vid.codec == "h264"
                and vid.bitrate < 15000000
            ):
                logger.info(f"Skipping low-quality file: {vid} ")
                progress.increment()
                shutil.copy2(vid.path, os.path.join(outdir.path, f"_{vid.basename}"))
                sleep(1)  # Give us a buffer to KeyboardIntterupt in case of undesred behaviour
                continue

            # for k, v in RENAME_SPEC.items():
            #     if k in vid.basename:
            #         output_file_name = f"{v}{vid.capture_date}".replace(" ", "_")
            output_file_path = os.path.join(outdir.path, f"_{vid.basename}")
            output_file_object = Video(output_file_path)
            try:
                compressed_files.append(vid.compress(output=output_file_path))
                size_before += vid.size
                size_after += output_file_object.size
                original_files.append(vid)

                print(
                    "Size:".ljust(10), f"{vid.size_human:<25} : {output_file_object.size_human:<25}"
                )
                print(
                    "Bitrate:".ljust(10),
                    f"{vid.bitrate_human:<25} : {output_file_object.bitrate_human:<25}",
                )

            except Exception as e:
                cprint(
                    f"\n{vid.basename} could not be converted. Error code: {e}",
                    fg.red,
                    style.bold,
                )

            progress.increment()
    # Notify user of completion
    cprint("\nBatch conversion completed.", fg.green)
    return original_files, compressed_files, size_before, size_after


if __name__ == "__main__":
    args = parse_arguments()
    try:
        old_files, new_files, before, after = main(args.INPUT, args.OUTPUT, args.num)
        if not old_files or not new_files:
            cprint("Nothing to convert. Exiting...", fg.yellow)
            exit()
    except KeyboardInterrupt:
        cprint("KeyboardInterrupt", fg.red)
        exit(127)

    space_saved = Converter(before - after)

    cprint(f"\nSpace saved: {space_saved}", fg.green, style.bold)
    if not args.keep:
        # remove old uncompressed files
        for file in old_files:
            try:
                os.remove(file.path)
            except OSError as e:
                print(e)  # remove error message
            except Exception:
                pass
