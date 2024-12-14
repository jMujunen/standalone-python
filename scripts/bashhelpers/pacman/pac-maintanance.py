#!/usr/bin/env python3

import argparse
import os
import subprocess
import sys

from Color import cprint, style

# TODO: Implement script to automated system maintenance
# - [x] Clean cache
# - [x] Prune journal
# - [x] Remove orphans
# - [ ] Empty /var/lib/coredump
# - [ ] List old unused packages
# - [ ] Find old files
# - [x] pacman -Qkk > /dev/null


def clean_cache() -> int:
    """Clean the package cache."""
    return os.system("sudo pacman -Scc")


def prune_journal() -> int:
    """Prune the journal to keep only the last two days."""
    return os.system("sudo journalctl --vacuum-time=2d")


def rm_orphans() -> int:
    """Remove orphaned packages."""
    return_code = os.system("sudo pacman -Rs $(pacman -Qtdq) 2> /dev/null")
    return 0 if return_code in {0, 256} else return_code


def check_file_properties() -> int:
    """Check file properties."""
    cprint("Checking file properties...", style.bold, style.underline)
    return os.system("pacman -Qkk > /dev/null")


def broken(*args) -> str:
    """List broken packages."""
    cprint("Listing broken packages...", style.bold, style.underline)
    arguments = ["--file-properties", "--recursive", *args]
    return subprocess.getoutput(["sudo", "paccheck", "--list_broken", *arguments])


def prune_core_dump() -> int:
    """Remove core dump files."""
    return os.system("rm -f /var/lib/systemd/coredump/*")


def main(args: argparse.Namespace):
    all_actions = {
        "clean": clean_cache,
        "prune": prune_journal,
        "orphans": rm_orphans,
        "check": lambda x: (check_file_properties(), broken(*x)),
        "coredump": prune_core_dump,
    }
    return sum(action() for action in all_actions.values() if args.__dict__[action.__name__])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Automate system maintenance tasks")
    parser.add_argument(
        "--check",
        help="Additional arguments for paccheck",
        required=False,
        nargs="*",
        choices=[
            "file-properties",
            "db-files",
            "checksum",
            "deps",
            "opt-deps",
        ],
        default=[],
    )
    parser.add_argument(
        "--skip",
        help="Skip the specified actions",
        required=False,
        nargs="*",
        choices=[
            "prune",
            "check",
            "clean",
        ],
        default=["check"],
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    sys.exit(main(args))
