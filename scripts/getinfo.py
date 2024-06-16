#!/usr/bin/env python3
"""Prints the total count of each file type in a given directory"""

import os
import sys

from ExecutionTimer import ExecutionTimer

DIRECTORY = os.getcwd()

file_types = {
    "img": [
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".heic",
        ".nef",
        ".webp",
        "svg",
    ],
    "doc": [".pdf", ".doc", ".docx", ".txt", ".odt", ".pptx"],
    "video": [".mp4", ".avi", ".mkv", ".wmv", ".webm", ".m4v"],
    "audio": [
        ".3ga",
        ".aac",
        ".ac3",
        ".aif",
        ".aiff",
        ".alac",
        ".amr",
        ".ape",
        ".au",
        ".dss",
        ".flac",
        ".flv",
        ".m4a",
        ".m4b",
        ".m4p",
        ".mp3",
        ".mpga",
        ".ogg",
        ".oga",
        ".mogg",
        ".opus",
        ".qcp",
        ".tta",
        ".voc",
        ".wav",
        ".wma",
        ".wv",
    ],
    "zip": [
        ".zip",
        ".rar",
        ".tar",
        ".bz2",
        ".7z",
        ".gz",
        ".xz",
        ".tar.gz",
        ".tgz",
        ".zipx",
    ],
    "raw": [".cr2", ".nef", ".raf", ".mov"],
    "text": [".txt", ".md", ".ini", ".log", ".json", ".csv", ".xml"],
    "code": [
        ".py",
        ".bat",
        ".sh",
        ".c",
        ".cpp",
        ".h",
        ".java",
        ".js",
        ".ts",
        ".php",
        ".html",
        ".css",
        ".scss",
    ],
    "other": [],  # For any other file type
    "dupes": [],  # For duplicate files
}


def count_file_types(directory):
    file_types = {}

    for root, dirs, files in os.walk(directory):
        for file in files:
            file_name, file_extension = os.path.splitext(file)
            if file_extension:
                file_extension = file_extension[1:]  # remove the dot from the extension
                if file_extension in file_types:
                    file_types[file_extension] += 1
                else:
                    file_types[file_extension] = 1

    return file_types


if __name__ == "__main__":
    if len(sys.argv) > 1:
        DIRECTORY = "".join(sys.argv[1:])
    with ExecutionTimer():
        file_type_counts = count_file_types(DIRECTORY)
        for file_type, count in file_type_counts.items():
            print("{:<20} {:>10}".format(file_type, count))
