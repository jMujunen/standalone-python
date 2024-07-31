#!/usr/bin/env python3

import os
import sys
import subprocess
import argparse

from Color import cprint, style

# TODO: Implement script to automated system maintenance
# - [x] Clean cache
# - [x] Remove sys logs
# - [x] Remove orphans
# - [ ] List old unused packages
# - [ ] Find old files
# - [x] pacman -Qkk > /dev/null


def clean_cache() -> int:
    """Clean the package cache."""
    return os.system("sudo pacman -Scc")


def clean_syslogs() -> int:
    return os.system("sudo journalctl --vacuum-time=2d")


def rm_orphans() -> int:
    return_code = os.system("sudo pacman -Rs $(pacman -Qtdq) 2> /dev/null")
    return 0 if return_code == 0 or return_code == 256 else return_code


def check_file_properties() -> int:
    return os.system("pacman -Qkk > /dev/null")


def list_broken(*args) -> str:
    if not args:
        args = ["--file-properties", "--recursive"]
    return subprocess.getoutput(["sudo", "paccheck", "--list_broken", *args])


def main(args: argparse.Namespace) -> int:
    cc_code = clean_cache()
    cs_code = clean_syslogs()
    ro_code = rm_orphans()
    cprint("Checking file properties...", style.bold, style.underline)
    cfp_code = check_file_properties()
    cprint("Listing broken packages...", style.bold, style.underline)
    list_broken(args.paccheck)
    return cc_code + cs_code + ro_code + cfp_code


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Automate system maintenance tasks")
    parser.add_argument(
        "--list_broken",
        help="Additional arguments for paccheck",
        nargs="*",
        required=False,
        type=list,
        choices=[
            "file-properties",
            "recursive",
            "db-files",
            "all",
            "checksum",
            "deps",
            "opt-deps",
        ],
        default=[],
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    sys.exit(main(args))
