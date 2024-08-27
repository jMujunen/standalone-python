#!/usr/bin/env python3

import argparse
import os


def parse_args():
    """
    Parse the command-line arguments for image resizing.

    Args:
        None

    Returns:
        parsed arguments from the command line
    """
    parser = argparse.ArgumentParser(
        description="Modify file extensions in bulk",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("DIR", help="Working Directory - Default=cwd", default=".")
    parser.add_argument("-o", "--old_extention", help="Old extention/file type - (jpg, py)")
    parser.add_argument("-n", "--new_extention", help="New extention/file type - Default = None")

    parser.add_argument(
        "-r",
        "--recursive",
        help="Act recursively for entire tree in DIR",
        action="store_true",
    )

    return parser.parse_args()


def main(args):
    old_extention = args.old_extention
    new_extention = args.new_extention
    if new_extention is None:
        new_extention = ""
    directory = args.DIR
    if args.recursive:
        for root, _dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(old_extention):
                    os.rename(
                        os.path.join(root, file),
                        os.path.join(root, file).replace(old_extention, new_extention),
                    )
    else:
        for file in os.listdir(directory):
            if file.endswith(old_extention):
                os.rename(
                    os.path.join(directory, file),
                    os.path.join(directory, file).replace(old_extention, new_extention),
                )


if __name__ == "__main__":
    main(parse_args())
