#!/usr/bin/env python3

"""Batch process all .mp4 files in a directory."""

import argparse
import os
import shutil
import subprocess

from Color import cprint, fg, style
from ExecutionTimer import ExecutionTimer
from fsutils import Dir, Video
from ProgressBar import ProgressBar
from size import Converter


def parse_arguments() -> argparse.Namespace:
    """Parse args."""
    parser = argparse.ArgumentParser(description="Batch process all .mp4 files in a directory")
    parser.add_argument(
        "input_directory",
        help="Input directory",
    )
    parser.add_argument("output_directory", help="Output directory")
    parser.add_argument(
        "--rate",
        help="Ensure bitrate (per second) is under this value\n\nNOT IMPLEMENTED",
        default="500000",
        type=int,
    )
    return parser.parse_args()


def main(
    input_directory: str,
    output_directory: str,
    rate: int,
) -> tuple[None | list[Video], None | list[Video]]:
    # List of file objects
    old_files = []
    new_files = []
    input_dir = Dir(input_directory)
    outdir = Dir(output_directory)

    try:
        # for folder_path in indir.rel_directories:
        # Create the output directories if they don't exist
        os.makedirs(outdir.path, exist_ok=True)
    except OSError as e:
        print(f"[\033[31m Error creating output directory '{outdir}': {e} \033[0m]")
        exit(1)

    # Initialize progress bar
    number_of_files = len(input_dir) + 1

    with ProgressBar(number_of_files) as progress:
        # Loop through all files in input directory
        for item in input_dir:
            progress.increment()
            if isinstance(item, Video):
                try:
                    # Define the output file path
                    output_file_path = os.path.join(outdir.path, item.basename)
                except Exception as e:
                    cprint(f"\n{e}", fg.red, style.underline)
                    continue

                # Check if the output file already exists
                if os.path.exists(output_file_path):
                    output_file_object = Video(output_file_path)
                    # If metadata is the same but size if different, its already compressed so skip
                    # and flag for removal of old file
                    if (
                        output_file_object.metadata == item.metadata
                        and output_file_object.size != item.size
                    ):
                        old_files.append(item)
                        new_files.append(output_file_object)
                        continue
                    elif output_file_object.is_corrupt:
                        os.remove(output_file_object.path)
                    elif (
                        output_file_object.basename == item.basename
                        and not output_file_object.is_corrupt
                        and item.size != output_file_object.size
                    ):
                        count = 0
                        # Loop until a unique name is found
                        while True:
                            try:
                                print(output_file_object.metadata)
                                print(output_file_object.bitrate)
                                print(output_file_object.size)
                                print(output_file_object.basename)
                                print("-------------")
                                print(item.metadata)
                                print(item.bitrate)
                                print(item.size)
                                print(item.basename)
                                # Rename the file: "input_file.mp4" -> "input_file_1.mp4"
                                new_path = f"{output_file_path[:-4]}_{count!s}.mp4"
                                shutil.move(item.path, new_path)
                                item = Video(new_path)
                                break
                            except FileExistsError:
                                count += 1
                                continue
                    # If all else fails, something was not accounted for
                    else:
                        (
                            os.remove(item.path)
                            if not item.is_corrupt
                            else cprint(
                                "FATAL ERROR: Manual intervention required",
                                fg.red,
                                style.underline,
                            )
                        )
                        continue
                # ffmpeg -i input.mp4 -c:v h264_nvenc -preset slow -crf 23 -b:v 0 -vf scale=1280:720 output.mp4
                # Run ffmpeg command for each file
                if item.bitrate < rate:
                    continue
                result = subprocess.run(
                    f'ffmpeg -i "{item.path}" -c:v hevc_nvenc -crf 20 -qp 20 "{output_file_path}"',
                    # f'ffmpeg -i "{item.path}" -c:v h264_nvenc -crf 18 -qp 28 "{output_file_path}"',
                    shell=True,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                result = result.returncode
                output_file_object = Video(output_file_path)

                # Check if conversion was successful and do a few more checks for redundancy
                if result == 0 and not item.is_corrupt and not output_file_object.is_corrupt:
                    old_files.append(item)
                    new_files.append(output_file_object)

                else:
                    cprint(
                        f"\n{item.basename} could not be converted. Error code: {result}",
                        fg.red,
                        style.bold,
                    )
            else:
                # Not a video, skip
                pass
    # Notify user of completion
    cprint("\nBatch conversion completed.", fg.green)
    return old_files, new_files


if __name__ == "__main__":
    # Context manager is perfect for an Execution timer
    with ExecutionTimer():
        args = parse_arguments()
        # Run the main function
        old_files, new_files = main(args.input_directory, args.output_directory, int(args.rate))
        if not old_files or not new_files:
            cprint("Nothing to convert. Exiting...", fg.yellow)
            exit(1)

        # Output how much data was saved in the conversion
        total_preproccessed_size = 0
        total_processed_size = 0
        for vid in old_files:
            total_preproccessed_size += vid.size
        for vid in new_files:
            total_processed_size += vid.size

        space_saved = Converter(total_preproccessed_size - total_processed_size)

        cprint(f"\nSpace saved: {space_saved}", fg.green, style.bold)
        # Triple check validity of conversion and finally, remove old files
        for vid in new_files:
            if vid.is_corrupt:
                cprint(f"\n{vid.path} is corrupt", fg.red, style.underline)
                continue
            else:
                try:
                    os.remove(os.path.join(args.input_directory, vid.basename))
                except Exception as e:
                    cprint(f"\n{e}", fg.red, style.underline)
                    continue

        print()
