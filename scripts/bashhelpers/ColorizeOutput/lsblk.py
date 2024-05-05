#!/usr/bin/env python3

# lsblk.py - Colorize the output of lsblk

from Styler import Styler

# ^ regex = r"(sd[a-z]|vd[a-z]|hd[a-z]|nvme[0-9]n[0-9])"  # Regular expression to match device 
# ^ color_code = "31"  # Color code for red

lsblk_styler = Styler('lsblk')


print(lsblk_styler.colorized_command_output(
    lsblk_styler.set_style(
        r"(sd[a-z][^0-9]|nvme[0-9]n[0-9][^a-z0-9])", "31"))
)
