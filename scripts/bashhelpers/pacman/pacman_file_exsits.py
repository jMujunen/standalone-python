#!/usr/bin/env python3

import os
import re
import subprocess

path_regex = re.compile(r".*:\s([^\s]+).*")
confirm_regex = re.compile(r"[yY]|^$")
output = subprocess.run(
    "sudo pacman -Syu", shell=True, capture_output=True, text=True, check=False
).stderr.strip()

matches = re.findall(path_regex, output)

for match in matches:
    print(match)
reply = input("\033[33mRemove these files? [y/N]: \033[0m")

if reply and re.match(confirm_regex, reply):
    for match in matches:
        try:
            os.remove(match)
        except Exception as e:
            print(f"Error: {e}")
            continue
