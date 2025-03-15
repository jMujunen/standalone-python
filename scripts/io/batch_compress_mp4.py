#!/usr/bin/env python3
"""Batch process all .mp4 files in a directory."""

import argparse
import os
import re
import shutil
import sys
from pathlib import Path
from typing import Any

from Color import cprint, fg, style
from fsutils.dir import Dir
from fsutils.video import Video
from ProgressBar import ProgressBar
from size import Size
from ThreadPoolHelper import Pool
from fsutils.utils.mimecfg import FILE_TYPES


RENAME_SPEC = {
    "PLAYERUNKNOWN": "PUBG",
}


def main(
    input_dir: str, num: int | None = None, *filters
) -> tuple[list[Video], list[Video], int, int]:
    """Batch process all .mp4 files in a directory.

    Args:
        input_dir (str): If not specified, the current working directory is used.
        output_dir (str): If not specified, the current working directory is used.
        num (int): Number of files to process at once. Defaults to all.
        filters (list[str]): List of file extensions to filter by. Defaults to all
    """
    pool = Pool()

    videos = [vid for vid in Dir(input_dir).videos()[:num] if vid.suffix.lower() in filters]
    failed_conversions = []
    successful_conversions = []
    compressed_videos = []
    # Create the output directories if they don't exist

    if not videos:
        cprint(f"No videos found in '{input_dir}'", fg.yellow)
        sys.exit(1)

    template = "\n{file:<25} {before_color}{bitrate_before}{reset} -> {after_color}{bitrate_after:<20}{reset}({diff_color}{diff}{reset})"
    with ProgressBar(len(videos)) as pb:
        for video in videos:
            try:
                compressed = video.compress()
                successful_conversions.append(video)
                compressed_videos.append(compressed)
                size_diff = compressed.size - video.size
                if size_diff > 0:
                    size_diff = f"+{size_diff}"
                print(
                    template.format(
                        file=video.name,
                        before_color=fg.red,
                        after_color=fg.green,
                        diff_color=fg.orange,
                        reset=style.reset,
                        bitrate_before=video.bitrate_human,
                        bitrate_after=compressed.bitrate_human,
                        diff=size_diff,
                    )
                )
            except KeyboardInterrupt:
                cprint.error("Conversion interrupted by user.")
                break
            except Exception as e:
                cprint.error(f"Failed to compress {video.name}: {e:!r}")
                failed_conversions.append(video)
            pb.increment()
    size_before = sum(pool.execute(lambda x: x.size, successful_conversions, progress_bar=False))
    size_after = sum(pool.execute(lambda x: x.size, compressed_videos, progress_bar=False))
    # Notify user of completion
    cprint.success("\nBatch conversion completed.", fg.green)
    return successful_conversions, failed_conversions, size_before, size_after


def parse_arguments() -> argparse.Namespace:
    """Parse args."""
    parser = argparse.ArgumentParser(description="Batch process all .mp4 files in a directory")
    parser.add_argument(
        "INPUT",
        help="Input directory",
    )
    parser.add_argument(
        "-n",
        "--num",
        help="Number of of files to compress in one sitting",
        default=None,
    )
    parser.add_argument(
        "--keep",
        help="Keep original file",
        action="store_true",
        default=False,
    )
    subparsers = parser.add_subparsers(
        dest="filter", required=False, help="Specify a filter for the files to compress"
    )
    # Filter by codec
    codec_subparser = subparsers.add_parser("codec", help="Filter by codec")
    codec_subparser.add_argument(
        "codec",
        help="Only compress files with this codec",
        choices=["h264", "hevc", "mpeg4"],
    )

    # Filter by bitrate
    bitrate_subparser = subparsers.add_parser("bitrate", help="Filter by bitrate")
    bitrate_subparser.add_argument(
        "bitrate",
        type=int,
        help="Only compress files with a bitrate over this value",
    )

    # Filter by extension
    extension_subparser = subparsers.add_parser(
        "extension",
        help="Filter by file extension",
    )
    extension_subparser.add_argument(
        "extension",
        help="Only compress files with this extension (e.g., .mp4)",
        type=str,
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    print(args)
    # print(*vars(args).values())
    # exit()

    success, failed, size_before, size_after = main(args.INPUT, args.num, args.extension)
    if not success and failed:
        cprint.error("Failed to compress the following files:\n" + "\n".join(failed))
        sys.exit("\n".join(failed))
    elif not success and not failed:
        cprint("Nothing to convert. Exiting...", fg.yellow)
        sys.exit(0)

    space_saved = Size(size_before - size_after)

    cprint(f"\nSpace saved: {space_saved}", fg.green, style.bold)

    if not args.keep:
        # remove old uncompressed files
        print("Removing old uncompressed files...")
        for file in success:
            try:
                os.remove(file.path)
            except OSError as e:
                cprint.error(f"{e!r}")
            except Exception:  # noqa: S112
                continue
