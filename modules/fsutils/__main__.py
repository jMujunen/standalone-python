#!/usr/bin/env python3
import argparse
import sys
from fsutils import Log, Img, Video  # , File, Dir, obj, Exe


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Command line tool for fsutils.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command")

    # Log File Commands
    log_parser = subparsers.add_parser("log", help="Commands related to log files.")
    log_subparsers = log_parser.add_subparsers()

    compare_log_parser = log_subparsers.add_parser("compare", help="Compare two log files.")
    compare_log_parser.add_argument("file1", type=str, help="Path to the first log file.")
    compare_log_parser.add_argument("file2", type=str, help="Path to the second log file.")

    # Image File Commands
    image_parser = subparsers.add_parser("image", help="Commands related to image files.")
    image_subparsers = image_parser.add_subparsers()

    open_image_parser = image_subparsers.add_parser("open", help="Open an image file.")
    open_image_parser.add_argument("file_path", type=str, help="Path to the image file.")

    save_image_parser = image_subparsers.add_parser(
        "save", help="Save an image to a specified location."
    )
    save_image_parser.add_argument("file_path", type=str, help="Path to the image file.")
    save_image_parser.add_argument(
        "output_path", type=str, help="Output path where the image will be saved."
    )

    # Video File Commands
    video_parser = subparsers.add_parser("video", help="Commands related to video files.")
    video_subparsers = video_parser.add_subparsers()

    metadata_video_parser = video_subparsers.add_parser(
        "metadata", help="Extract metadata from a video file."
    )
    metadata_video_parser.add_argument("file_path", type=str, help="Path to the video file.")
    make_gif_video_parser = video_subparsers.add_parser(
        "makegif", help="Make a gif from a video file."
    )
    make_gif_video_parser.add_argument("file_path", type=str, help="Path to the video file.")
    make_gif_video_parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="Output path for the gif.",
        default="./output.gif",
        required=False,
    )
    make_gif_video_parser.add_argument(
        "-s",
        "--scale",
        type=int,
        default=500,
        help="Scale factor for the gif - (100-1000 is usually good).",
        required=False,
    )
    make_gif_video_parser.add_argument(
        "--fps",
        type=int,
        help="Frames per second for the gif.",
        default=24,
        required=False,
    )

    # Parse and execute arguments
    args = parser.parse_args()

    if args.command == "log":
        if args.subcommand == "compare":
            log1 = Log(args.file1)
            log2 = Log(args.file2)
            log1.compare(log2)

    elif args.command == "image":
        if args.subcommand == "open":
            # Initialize and render
            blob = Img(args.file_path)
            blob.render()
            return
        elif args.subcommand == "save":
            return 1
    elif args.command == "video":
        if args.subcommand == "metadata":
            metadata = Video(args.file_path).metadata
            print(metadata)
        elif args.subcommand == "makegif":
            blob = Video(args.file_path)
            return blob.make_gif(
                args.scale,
                args.fps,
                args.output,
            )
    else:
        parser.print_help()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
