#!/usr/bin/env python3
import os
import subprocess
import sys
from pathlib import Path
from ProgressBar import ProgressBar
from Color import cprint
from fsutils.dir import Dir

HOME = "/home/joona"

SRC_DIRS = [
    "Docs/Notes/Obsidian/All Notes",
    ".config/kitty",
    ".config/bat",
    ".config/hypr",
    ".config/waybar",
    ".config/VSCodium/User",
    ".dotfiles/",
    "scripts/",
    ".ipython/",
    ".config/mpv",
    ".mozilla/firefox/h76d4ruz.default-release",
]

TARGET_ROOT = "/mnt/hddred/rsync/linux-desktop/joona/"


def main(dirs: list[str]) -> None:
    """Sync the specified directories to the target root."""
    msgs = []
    # Check if the user is root
    if os.geteuid() != 0:
        print("This script must be run as root.")
        sys.exit(1)
    with ProgressBar(len(dirs)) as pb:
        for d in dirs:
            cmd_template = "rsync -auhX --compress-choice=none '{src}' '{dest}'"
            src = Path(HOME, d)
            target = Path(TARGET_ROOT, d) or Path(TARGET_ROOT, d)
            items = len(Dir(str(src)).files)
            if not target.exists():
                target.mkdir(parents=True, exist_ok=True)
            result = subprocess.getoutput(
                cmd_template.format(src=src, dest=target, items=items)
            )

            # Log the output of rsync command until the end of iterations
            msgs.append(result)
            pb.increment()
    print("\n\n".join(msgs))


if __name__ == "__main__":
    main(SRC_DIRS)
