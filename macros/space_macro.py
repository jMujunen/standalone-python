#!/usr/bin/env python3

# space_macro.py - Press SPACE 4 times with 10ms delay when \ is pressed

from time import sleep
import keyboard

def send_keys():
    keyboard.press('space')
    keyboard.release('space')
    sleep(0.05)
    keyboard.press('space')
    keyboard.release('space')
    sleep(0.05)
    keyboard.press('space')
    keyboard.release('space')
    sleep(0.05)
    keyboard.press('space')
    keyboard.release('space')


while True:
    try:
        keyboard.wait('\\')
        send_keys()
    except KeyboardInterrupt:
        break