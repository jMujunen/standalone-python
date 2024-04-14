#!/usr/bin/env python3

# count_hydra_attacks.py - Display a notification 1 tick before poison attack 
#                          for final hydra phase

import keyboard
from time import sleep
import subprocess
import sys

def main():
    while True:
        try:
            keyboard.wait('\\')
        except Exception as e:
            print(e)
            sys.exit(f'Error: {e}')
        else:
            tick = 0.6 * 4
            first_special = 3
            second_special = 10
            sleep(tick * first_special)
            send_notification()

            sleep(tick * second_special)
            send_notification()

def send_notification():
    try:
        notif = subprocess.run(
            'sudo -u joona DISPLAY=:0 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus notify-send  "Poison Attack!" --icon=com.jagex.Launcher --app-name=Hydra\ Special',
            shell=True
        )
    except Exception as e:
        sys.exit(f'Error: {e}')


if __name__ == '__main__':
    main()