#!/usr/bin/env python3

# lsblk.py - Colorize the output of lsblk

from Styler import Styler
import sys

# regex = r"(sd[a-z]|vd[a-z]|hd[a-z]|nvme[0-9]n[0-9])"  # Regular expression to match device 
# color_code = "31"  # Color code for red


lsblk_styler = Styler('lsblk -af')

# TODO
# * bg=$(tput setab 240)
# * fg=$(tput setaf 3)

print(lsblk_styler.colorized_command_output([
    # Match device names
    lsblk_styler.set_style(
        r"(sd[a-z][^0-9]|nvme[0-9]n[0-9][^a-z0-9])", "33"),
    # Match Partitions
    lsblk_styler.set_style(
        r"(sd[a-z][0-9]|nvme[0-9]n[0-9][a-z0-9]+)", "38;2;93;163;209"),
    # Match digit percentages
    lsblk_styler.set_style(
        r"(.?\d+%)", "32"),
    # Match header
    lsblk_styler.set_style(
        r"^\s?([A-Z]+%?)\s", "30;38;2;80;80;80"
    )
]))
