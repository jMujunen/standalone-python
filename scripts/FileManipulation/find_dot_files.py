#!/usr/bin/env python3

# find_dot_files.py - Find dot files in home directory

import os
import sys
import subprocess
import glob
#import argparse
import re



def main():
    # Get the user's home directory
    home_dir = os.path.expanduser("~")

    # Find all dot files in the entire home directory tree 
    # using subprocess `find`
    dot_files = subprocess.run(
        f"find {home_dir} -name '.*' -type f",
        shell=True,
        capture_output=True,
        text=True
    )
    

    rc_files = subprocess.run(
        f"find {home_dir} -name '*rc' -type f",
        shell=True,
        capture_output=True,
        text=True
    )

    # Print the dot files
    print("Dot files:")

