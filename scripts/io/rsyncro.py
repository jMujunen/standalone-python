#!/usr/bin/env python3
import os
import subprocess
import sys
from pathlib import Path

from Color import cprint
from fsutils.compiled._DirNode import Dir

HOME = "/home/joona"

SRC_DIRS = [
    "Docs/Notes/Obsidian/All Notes",
    ".config/kitty",
    ".config/bat",
    ".config/VSCodium/User",
    ".dotfiles",
    "scripts",
    "Logs",
    ".ipython",
]

TARGET_ROOT = "/mnt/hddred/rsync/linux-desktop/joona/"


def main(dirs: list[str]) -> None:
    """Sync the specified directories to the target root."""
    # Check if the user is root
    if os.geteuid() != 0:
        print("This script must be run as root.")
        sys.exit(1)

    for d in dirs:
        cmd_template = (
            "rsync -auhX --compress-choice=none {src} {dest} | python3 -m ProgressBar {items}"
        )
        src = Path(HOME, d)
        target = Path(TARGET_ROOT, d) or Path(TARGET_ROOT, d)
        items = len(Dir(src).files)
        if not target.exists():
            target.mkdir(parents=True, exist_ok=True)
        result = subprocess.getoutput(cmd_template.format(src=src, dest=target, items=items))
        sys.stdout.write(result + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main(SRC_DIRS)
