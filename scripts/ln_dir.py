#!/usr/bin/env python3

import argparse
import os
import re

from fsutils import FileManager


def parse_args():
    parser = argparse.ArgumentParser(
        description="This script is used as a redneck way to hardlink a directory and its subdirectories",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("FileManager", help="The directory to be hardlinked.", default=".")
    parser.add_argument(
        "-o",
        "--output",
        help="path to the link: Default: pwd",
        required=False,
        default=os.getcwd(),
    )
    parser.add_argument(
        "-p",
        "--pattern",
        help="The pattern (PCRE) to match files against.",
        default=".*",
    )
    return parser.parse_args()


def mklinks(src, dst, pattern):
    """
    Recursively hardlink files in the src directory

    Creates a link to each file in the src directory to the dst directory.
    Each time this method finds a directory, it calls itself creating recursion.

    Parameters:
    ----------
        output_path (str): path to the directory to be cleaned up
        src (str): path to the source directory
        dst (str): path to the destination directory
        pattern (str): PCRE pattern to match files against
    """

    for file in os.listdir(src):
        file_path = os.path.join(src, file)
        if os.path.isfile(file_path) and re.match(pattern, file):
            link = os.path.join(dst, file)
            print(f"Linking {link} to {os.path.join(src, file)}")
            try:
                # Attempt to create a hardlink
                os.link(os.path.join(src, file), link)
            except FileExistsError:
                print("File already exists")
            except PermissionError:
                print("Permission denied")
            except OSError:
                print("Failed to create link")
            except Exception:
                print("Unknown error")
        elif os.path.isdir(os.path.join(src, file)):
            # Recursively call this method for directories
            mklinks(os.path.join(src, file), os.path.join(dst, file), pattern)


def cleanup(output_path):
    """
    Clean up empty directories.
    Some directories may be empty due to creating directories first, asking questions later.
    This is dependant on the pattern provided since some patterns will return more files than others.
    Hence, remove empty directories

    Parameters:
    ----------
        output_path (str): path to the directory to be cleaned up
    """
    for root, _dirs, _files in os.walk(output_path, topdown=False):
        directory = FileManager(root)
        if directory.is_empty:
            print(f"Removing empty directory: {root}")
            try:
                os.rmdir(root)
            except OSError:
                print(f"Failed to remove empty directory: {root}")
                continue
            except Exception as e:
                print(f"Unexpected error: {e}")
                continue
        else:
            print(f"Keeping non-empty directory: {root}")


def main(input_path, output_path, pattern):
    """
    This script is used as a redneck way to hardlink a directory and its subdirectories.

    It recreates the directory tree of the input directory and then hardlinks all files
    that match a given pattern in it to the recreated tree.

    Parameters:
    ----------
        input_path (str): path to the directory to be hardlinked
        output_path (str): path to the link: Default: pwd
        pattern (str): The pattern (PCRE) to match files against.
    """
    FileManager = FileManager(input_path)
    # Create parents for the output FileManager if they doisn't exist
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    # Create the directory tree for output path
    for folder in FileManager.rel_directories:
        try:
            new_folder = os.path.abspath(os.path.join(output_path, folder))
            os.makedirs(new_folder, exist_ok=True)
        except Exception as e:
            print("Error while processing directory", folder, ":", str(e))
    # Finally, hardlink the files that match the given pattern
    mklinks(input_path, output_path, pattern)

    # Cleanup empty directories in output path
    cleanup(output_path)


# Example
if __name__ == "__main__":
    args = parse_args()
    main(args.FileManager, args.output, args.pattern)
