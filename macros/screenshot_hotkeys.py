#!/usr/bin/env python3

import re
import datetime
import subprocess
import keyboard

# Take screenshot of entire desktop
def on_printscreen():
    time = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    subprocess.run(
        f'spectacle -b --fullscreen --ouput ~/Pictures/Screenshots/Desktop-{time}.png',
        shell=True)

# Take screenshot of a region
def on_alt_printscreen():
    time = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    subprocess.run(
        f'spectacle -b --region --output ~/Pictures/Screenshots/Region-{time}.png', 
        shell=True)

# Take screenshot of a window
def on_shift_printscreen():
    time = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    window_output = subprocess.run(
        'xwininfo | grep "Window id: " | cut -d" " -f4',
        shell=True,
        text=True,
    ).stdout.strip()
    
    print(window_output)

    subprocess.run(
        f'spectacle -b --activewindow --output ~/Pictures/Screenshots/Window-{time}.png',
    )
    subprocess.run('screenshot.sh --shift', shell=True)

# Capture focused screen
def on_win_printscreen():
    time = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    subprocess.run(
        f'spectacle -b --focused --output ~/Pictures/Screenshots/Focused-{time}.png', 
        shell=True)
def main():
    keyboard.add_hotkey('printscn', on_printscreen)


if __name__ == '__main__':
    main()