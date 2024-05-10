#!/usr/bin/env python3

# presence_detect.py - Presence Detection. Bluetooth and WiFi presence detection

import threading
import time
import subprocess
import sys
import nmap
from Notification import Notification
import datetime
from time import sleep
from kde_sms import SMS

class Entity:
    def __init__(self, name, address):
        self.name = name
        self.address = address
        self.last_seen = 0
        self.presence = False

    def __str__(self):
        return self.name

    def ping(self):
        try:
            ping_output = subprocess.check_output(
                f'ping -c 1 -W 2 {self.address}',
                shell=True
            )
            self.presence = True
        except subprocess.CalledProcessError:
            self.presence = False
        return self.presence


pixel = Entity("Pixel", "10.0.0.148")
notify = Notification("Presence", "Pixel is here!")

while True:
    try:
        if pixel.ping():
            pixel.last_seen = time.time()
            print(f"Last seen:{datetime.datetime.fromtimestamp(pixel.last_seen)}")
            notify = Notification("Presence", "Pixel is here!")
            notify.show()
            print(send_sms(6042265455, "Pixel is here!"))
            sleep(3)
            continue
    except Exception as e:
        print(e)
    sleep(0.5)
