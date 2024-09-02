#!/usr/bin/env python3
"""Batch process all .mp4 files in a directory."""

import argparse
import os
import shutil

from Color import cprint, fg, style
from fsutils import Dir, Video
from size import Size
from ThreadPoolHelper import Pool

RENAME_SPEC = {
    "PLAYERUNKNOWN": "PUBG",
}


def compress_file(file: Video, output_dir: str) -> Video | None:
    """Process a single .mp4 file."""
    output_file_path = os.path.join(output_dir, f"_{file.basename}")
    output_file_object = Video(output_file_path)
    if output_file_object.exists and output_file_object.size < file.size:
        return
        # TODO: Implement FFMpegManager context manager
    try:
        compressed = file.compress(output=output_file_path)
        print("Size:".ljust(10), f"{file.size_human:<25} : {output_file_object.size_human:<25}")
        print(
            "Bitrate:".ljust(10),
            f"{file.bitrate_human:<25} : {output_file_object.bitrate_human:<25}",
        )
        return compressed
    except Exception as e:
        cprint(
            f"{e!r}: {file.basename} could not be converted ({e})",
            fg.red,
            style.bold,
        )


def process_file(file: Video, output_dir: str) -> Video | None:
    """If video codec is HEVC and bitrate is greater than 30MB/s, compress;
    otherwise, move it to the output directory."""
    try:
        if file.bitrate > 30000000:
            return file
        else:
            shutil.move(
                file.path,
                os.path.join(output_dir, f"_{file.basename}"),
                copy_function=shutil.copy2,
            )
    except Exception as e:
        cprint(f"\n{file.basename} could not be processed. Error code: {e}", fg.red, style.bold)
    return


def main(input_dir: str, output_dir: str, num: int) -> tuple[list[Video], list[Video], int, int]:
    # formula = (S - s) / (B - b)
    #
    # S = Originial size
    # s = Compressed size
    # -------------------
    # B = Original bitrate
    # b = compressed bitrate

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
    # formula = (S - s) / (B - b)
    # Initialize progress bar vars
    number_of_files = len(videos)
    cprint(f"1/{number_of_files}", style.bold, style.underline, end="\n\n")
    pool = Pool()
    for result in pool.execute(process_file, videos, outdir.path, progress_bar=True):
        if result is not None:
            compressed = compress_file(result, outdir.path)
            if compressed is not None and os.path.exists(compressed.path):
                compressed_files.append(compressed)
                size_diff, bitrate_diff = (
                    (result.size - compressed.size),
                    (result.bitrate - compressed.bitrate),
                )
                if any((size_diff < 0, bitrate_diff < 0)):
                    size_ratio = "\033[31mError: filesize / bitrate increased\033[0m"
                else:
                    size_ratio = size_diff / bitrate_diff
                print(
                    f"""File size decreased {style.bold}{size_ratio}x{style.reset} more than bitrate
                    Bitrate: Original:{fg.red}{Size(result.bitrate)} {style.reset} -> {fg.green}{Size(compressed.bitrate)}{style.reset})
                    File Size: Original:{fg.red}{Size(result.size)}  {style.reset} -> {fg.green}{Size(compressed.size)}{style.reset}
                    """
                )
                print(f"Quality: {compressed.num_frames}")
                original_files.append(result)
                size_before += result.size
                size_after += compressed.size
    # Notify user of completion
    cprint("\nBatch conversion completed.", fg.green)
    return original_files, compressed_files, size_before, size_after


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

    space_saved = Size(before - after)

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
