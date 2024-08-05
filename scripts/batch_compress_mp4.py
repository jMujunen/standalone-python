#!/usr/bin/env python3

"""Batch process all .mp4 files in a directory."""

import argparse
import os
import shutil

from Color import cprint, fg, style
from ExecutionTimer import ExecutionTimer
from fsutils import Dir, Video
from ProgressBar import ProgressBar
from size import Converter

RENAME_SPEC = {
    "PLAYERUNKNOWN": "PUBG",
}


def parse_arguments() -> argparse.Namespace:
    """Parse args."""
    parser = argparse.ArgumentParser(description="Batch process all .mp4 files in a directory")
    parser.add_argument(
        "input_directory",
        help="Input directory",
    )
    parser.add_argument("output_directory", help="Output directory")
    return parser.parse_args()


def main(
    input_directory: str,
    output_directory: str,
) -> tuple[list[Video], list[Video], int, int]:
    # List of file objects
    original_files = []
    compressed_files = []

    size_before = 0
    size_after = 0

    videos = Dir(input_directory).videos
    outdir = Dir(output_directory)

    try:
        # for folder_path in indir.rel_directories:
        # Create the output directories if they don't exist
        os.makedirs(outdir.path, exist_ok=True)
    except OSError as e:
        print(f"[\033[31m Error creating output directory '{outdir}': {e} \033[0m]")
        exit(1)

    # Initialize progress bar
    number_of_files = len(videos)
    cprint(f"1/{number_of_files}", style.bold, style.underline, end="\n\n")

    with ProgressBar(number_of_files) as progress:
        for vid in videos:
            print("\n")
            cprint(vid.basename, style.bold, style.underline)
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
    # Context manager is perfect for an Execution timer
    with ExecutionTimer():
        args = parse_arguments()
        # Run the main function
        old_files, new_files, before, after = main(args.input_directory, args.output_directory)
        if not old_files or not new_files:
            cprint("Nothing to convert. Exiting...", fg.yellow)
            # exit(1)

        # Output how much data was saved in the conversion
        # total_preproccessed_size = 0
        # total_processed_size = 0
        # for vid in old_files:
        #     total_preproccessed_size += vid.size
        # for vid in new_files:
        #     total_processed_size += vid.size

        space_saved = Converter(before - after)

        cprint(f"\nSpace saved: {space_saved}", fg.green, style.bold)
        with open("./compression_log.log", "w") as f:
            f.write("\n".join([i.path for i in old_files]))
        print()
