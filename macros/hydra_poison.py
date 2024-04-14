#!/usr/bin/env python3

# space_macro.py - Press SPACE 4 times with 10ms delay when \ is pressed
import os
from time import sleep
import keyboard
import subprocess

TICK = 0.6
ATTACK_SPEED = TICK * 4
FIRST_SPEC = 3
SECOND_SPEC = 10
MINUS_FADE_TIME = 2

WIN_MARGIN = 60

# colors
WIN_COLOR = "#282828"
TEXT_COLOR = "#ffffff"

# Base64 icons
img_error = b'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAMAAABEpIrGAAAAA3NCSVQICAjb4U/gAAAACXBIWXMAAADlAAAA5QGP5Zs8AAAAGXRFWHRTb2Z0d2FyZQB3d3cuaW5rc2NhcGUub3Jnm+48GgAAAIpQTFRF////20lt30Bg30pg4FJc409g4FBe4E9f4U9f4U9g4U9f4E9g31Bf4E9f4E9f4E9f4E9f4E9f4FFh4Vdm4lhn42Bv5GNx5W575nJ/6HqH6HyI6YCM6YGM6YGN6oaR8Kev9MPI9cbM9snO9s3R+Nfb+dzg+d/i++vt/O7v/fb3/vj5//z8//7+////KofnuQAAABF0Uk5TAAcIGBktSYSXmMHI2uPy8/XVqDFbAAAA8UlEQVQ4y4VT15LCMBBTQkgPYem9d9D//x4P2I7vILN68kj2WtsAhyDO8rKuyzyLA3wjSnvi0Eujf3KY9OUP+kno651CvlB0Gr1byQ9UXff+py5SmRhhIS0oPj4SaUUCAJHxP9+tLb/ezU0uEYDUsCc+l5/T8smTIVMgsPXZkvepiMj0Tm5txQLENu7gSF7HIuMreRxYNkbmHI0u5Hk4PJOXkSMz5I3nyY08HMjbpOFylF5WswdJPmYeVaL28968yNfGZ2r9gvqFalJNUy2UWmq1Wa7di/3Kxl3tF1671YHRR04dWn3s9cXRV09f3vb1fwPD7z9j1WgeRgAAAABJRU5ErkJggg=='

def send_notification():
    notify = Notification.display_notification(
        "Special Attack", 
        "Poison Attack!", 
        img_error,
        1000,
        True,
        0.9,
        (1920, 800),
        )
    

print('Waiting for keystroke...')
count = 0
while True:
    try:

        notfy = subprocess.run(
            'sudo -u joona DISPLAY=:0 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus notify-send "Hello world!" "This is an example notification."',
            shell=True,
        )

        keyboard.wait('\\')
        count += 1
        os.system('clear')
        print(f'Hotkey pressed {count} times', end='\r')
    except KeyboardInterrupt:
        break