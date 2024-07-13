#!/usr/bin/env python3

import os
import sys
import subprocess

# TODO: Implement script to automated system maintanance
# - [x] Clean cache
# - [x] Remove sys logs
# - [x] Remove orphans
# - [ ] List old unused packages
# - [ ] Find old files
# - [ ] pacman -Qkk > /dev/null


def clean_cache() -> int:
    """Clean the package cache."""
    return os.system("sudo pacman -Scc")


def clean_syslogs() -> int:
    return os.system("sudo journalctl --vacuum-time=2d")


def rm_orphans() -> int:
    return_code = os.system("sudo pacman -Rs $(pacman -Qtdq)")
    return 0 if return_code == 0 or return_code == 256 else return_code

def main() -> None:
    clean_cache()
    clean_syslogs()
    rm_orphans()

if __name__ == "__main__":
    main()
