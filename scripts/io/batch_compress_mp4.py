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
from fsutils.dir import Dir,
from fsutils.video import Video
from ProgressBar import ProgressBar
from size import Size
from ThreadPoolHelper import Pool

RENAME_SPEC = {
    "PLAYERUNKNOWN": "PUBG",
}


def main(input_dir: str, output_dir: str, num: int, *filters):
    pool = Pool()

    outdir = Dir(output_dir)

    videos = [vid for vid in Dir(input_dir).videos()[:num] if vid.suffix in filters]
    failed_conversions = []
    successful_conversions = []
    compressed_videos = []
    # Create the output directories if they don't exist
    try:
        outdir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        print(f"[\033[31m Error creating output directory '{outdir}': {e} \033[0m]")
        sys.exit(1)

    if not videos:
        cprint(f"No videos found in '{input_dir}'", fg.yellow)
        sys.exit(1)

    template = "{file:<25}: ({before_color}{size_before:<10} | {bitrate_before:<10}{reset1}) -> ({after_color}{size_after:<10} | {bitrate_after}{reset2})"
    with ProgressBar(len(videos)) as progress:
        for video in videos:
            try:
                result = video.compress()
                successful_conversions.append(video)
                compressed_videos.append(result)
                print(
                    template.format(
                        file=video.name,
                        before_color=fg.red,
                        after_color=fg.green,
                        reset1=style.reset,
                        reset2=style.reset,
                        size_before=video.size_human,
                        bitrate_before=video.bitrate_human,
                        size_after=result.size_human,
                        bitrate_after=result.bitrate_human,
                    )
                )
            except Exception as e:
                cprint.error(f"Failed to compress {video.name}: {e:!r}")
                failed_conversions.append(video)
        progress.increment()
    size_before = sum(pool.execute(lambda x: x.size, videos, progress_bar=True))
    size_after = sum(pool.execute(lambda x: x.size, compressed_videos, progress_bar=True))
    # Notify user of completion
    cprint("\nBatch conversion completed.", fg.green)
    return successful_conversions, failed_conversions, size_before, size_after


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

    main(args.INPUT, args.OUTPUT, args.num, args.keep, ".mkv")
    try:
        success, failed, size_before, size_after = main(
            args.INPUT, args.OUTPUT, args.num, args.keep
        )
        if not success and failed:
            cprint.error("Failed to compress the following files:\n" + "\n".join(failed))
            sys.exit("\n".join(failed))
        elif not success and not failed:
            cprint("Nothing to convert. Exiting...", fg.yellow)
            sys.exit(0)
    except KeyboardInterrupt:
        cprint("KeyboardInterrupt", fg.red)
        sys.exit(127)

    space_saved = Size(size_before - size_after)

    cprint(f"\nSpace saved: {space_saved}", fg.green, style.bold)
    if not args.keep:
        # remove old uncompressed files
        for file in success:
            try:
                os.remove(file.path)
            except OSError as e:
                cprint.error(f"{e!r}")  # remove error message
            except Exception:
                pass
