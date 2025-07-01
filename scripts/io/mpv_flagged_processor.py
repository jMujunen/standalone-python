#!/usr/bin/env  python3
import logging
import sys
from pathlib import Path

from tqdm import tqdm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main(dest: str, *args) -> int:
    """For each file in stdin, read the filepaths from the file and move each one to dest."""
    cwd = "/mnt/hdd/sorted-webcam-clips/"
    dest_dir = Path(dest)
    print(dest)
    for i in tqdm(args):
        file = Path(i).resolve()
        if not file.exists():
            logger.warn(f"File {file} does not exist.")
            continue
        content = file.read_text().splitlines()
        for line in content:
            src_file = file.parent / line.strip()
            print(file.parent)
            print(src_file)
            print(file.parent, Path(line.strip()))
            if not src_file.exists():
                if src_file.name in list(dest_dir.glob("*")):
                    print("\033[33mFile exists in destination directory.\033[0m")
                    continue
                logger.warn(f"srcFile {src_file} does not exist.")
                continue
            dest_file = dest_dir / src_file.name
            try:
                src_file.rename(dest_file)
                print(f"Moved {src_file} to {dest_file}")
            except FileExistsError as e:
                logger.error(e)

    return 0


if __name__ == "__main__":
    dest = sys.argv[1]
    args = sys.argv[2:]
    sys.exit(main(dest, *args))
